from datetime import datetime, timedelta

from celery.utils.log import get_task_logger

from main import celery, db
from main.enums import ExpertState, SentinelRouteState, RouteState, RREConfig, QuestionState
from main.models.question_state import QuestionStateModel
from main.models.expert_state import ExpertStateModel
from main.models.question import QuestionModel
from main.models.expert_earning import ExpertEarningModel
from main.models.user_subscription_package import UserSubscriptionPackageModel
from main.models.route import RouteModel
from main.models.user import UserModel
from main.engines import rre, pusher
from main.libs import float_operator

logger = get_task_logger(__name__)


def compute_expert_state(expert_route):
    if expert_route.state == RouteState.BIDDING:
        return ExpertState.BIDDING
    if expert_route.state == RouteState.KING:
        return ExpertState.KING
    if expert_route.state == RouteState.WORKING:
        return ExpertState.WORKING
    return ExpertState.NOT_ROUTED


NO_KING_ROUTE_STATES = {
    SentinelRouteState.ROUTED,
    RouteState.TIMEOUT,
    RouteState.BIDDING,
    RouteState.SKIPPED,
}

HAS_KING_ROUTE_STATES = {
    SentinelRouteState.ROUTED,
    RouteState.TIMEOUT,
    RouteState.BIDDING,
    RouteState.SKIPPED,
    RouteState.LOST,
    RouteState.KING
}

FAILED_ROUTE_STATES = {
    SentinelRouteState.FAILED,
    RouteState.SKIPPED,
    RouteState.TIMEOUT,
}

WORKING_ROUTE_STATES = {
    SentinelRouteState.SUCCESS,
    RouteState.SKIPPED,
    RouteState.TIMEOUT,
    RouteState.LOST,
    RouteState.WORKING
}

RATING_ROUTE_STATES = {
    SentinelRouteState.SUCCESS,
    RouteState.SKIPPED,
    RouteState.TIMEOUT,
    RouteState.LOST,
    RouteState.RATING
}

COMPLETE_ROUTE_STATES = {
    SentinelRouteState.SUCCESS,
    RouteState.SKIPPED,
    RouteState.TIMEOUT,
    RouteState.LOST,
    RouteState.COMPLETE
}


def compute_question_state(question_routes):
    route_states = [route.state for route in question_routes]
    print('route_states', route_states)
    king_count = route_states.count(RouteState.KING)
    working_count = route_states.count(RouteState.WORKING)
    complete_count = route_states.count(RouteState.COMPLETE)

    assert king_count <= 1
    assert working_count <= 1
    assert complete_count <= 1
    assert king_count + working_count + complete_count <= 1

    route_states_set = set(route_states)
    print('route_states_set', route_states_set)

    if not route_states:
        return QuestionState.NOT_ROUTED

    if route_states_set.issubset(NO_KING_ROUTE_STATES):
        return QuestionState.NO_KING

    if route_states_set.issubset(HAS_KING_ROUTE_STATES):
        return QuestionState.HAS_KING

    if route_states_set.issubset(FAILED_ROUTE_STATES):
        return QuestionState.FAILED

    if route_states_set.issubset(RATING_ROUTE_STATES):
        return QuestionState.RATING

    if route_states_set.issubset(WORKING_ROUTE_STATES):
        return QuestionState.WORKING

    if route_states_set.issubset(COMPLETE_ROUTE_STATES):
        return QuestionState.COMPLETE


def compute_num_bidding(question_routes):
    num_bidding = 0
    for route in question_routes:
        if route.state == RouteState.BIDDING:
            num_bidding += 1

    return num_bidding


def _get_all_question_routes(question_id):
    """
    Get and return all routes of a question
    :param question_id:
    :return:
    """
    return RouteModel.query. \
        with_for_update(). \
        filter_by(question_id=question_id). \
        all()


def _get_route_by_state(routes, route_state):
    """
    Searching in a list of routes to find a route that has particular state
    :param routes:
    :param route_state:
    :return:
    """
    for route in routes:
        if route.state == route_state:
            return route
    return None


def _change_route_state(question_state, next_state):
    """
    Move current route state to the next state. Supported:
    - Working -> Rating
    :param question_state:
    :param next_state:
    :return:
    """
    assert question_state
    question_id = question_state.question_id
    question_routes = _get_all_question_routes(question_id)

    # Get current route state
    route_state = RouteState.WORKING
    current_route = _get_route_by_state(question_routes, route_state)
    if not current_route:
        raise Exception('Question not in the correct state')

    _state = next_state
    current_route.state = next_state
    question_state.state = compute_question_state(question_routes)
    current_route.expert_state.state = compute_expert_state(current_route)

    expert_earning = ExpertEarningModel(
        expert_id=current_route.expert_id,
        question_id=current_route.question_id,
        amount=current_route.bid_amount,
    )
    user = UserModel.query.get(question_state.user_id)
    user_subscription_package = UserSubscriptionPackageModel.query.filter_by(
        user_id=question_state.user_id,
        status="active"
    ).first()

    if user_subscription_package is None:
        if user.free_credit_balance > 0:
            user.free_credit_balance = user.free_credit_balance - 1
        elif user.paid_credit_balance > 0:
            user.paid_credit_balance = user.paid_credit_balance - 1

    db.session.add(user)
    db.session.add(expert_earning)
    db.session.commit()

    # Notify client that question is done
    pusher.trigger_question_done(question_id)


def _route_experts_to_question(question_state, expert_states):
    question_routes = RouteModel.query. \
        with_for_update(). \
        filter_by(question_id=question_state.question_id). \
        all()

    expert_states.sort(key=lambda e: e.expert_id)

    with db.session.no_autoflush:
        for expert_state in expert_states:
            route = RouteModel(
                expert_state=expert_state,
                question_state=question_state,
                state=RouteState.BIDDING,
            )
            db.session.add(route)
            expert_state.current_question_id = question_state.question_id
            expert_state.state = compute_expert_state(route)
            question_routes.append(route)

    question_state.state = compute_question_state(question_routes)
    question_state.num_bidding = compute_num_bidding(question_routes)


@celery.task()
def handle_chatting_timeout(question_id):
    # Get question state
    question_state = QuestionStateModel.query.get(question_id)

    if not question_state:
        raise Exception('Question not found')

    if question_state.state != QuestionState.WORKING:
        raise Exception('Question is not in working state')

    # Change state from answering to rating
    _change_route_state(question_state, RouteState.RATING)


@celery.task()
def handle_route_timeout(question_id, timeout=False):
    """
    Even though this function is called 'handle_route_timeout' there
    are in fact two cases where this function can be called.

    Case 1
    A routing timeout has occurred

        If there is a KING bidder, he should be routed to the chat
        otherwise we should mark it as failed.
        Non-kings who are still bidding should all be timed out

    Case 2
    No one is left bidding
    .i.e all experts's who we routed to have either bid or skipped, etc ...

        Same logic as in case 1 but no one is timed out
    """
    question_state = QuestionStateModel.query.get(question_id)
    assert question_state

    if question_state.state not in (QuestionState.NO_KING, QuestionState.HAS_KING):
        raise Exception('Question finished routing (1)')

    question_routes = RouteModel.query. \
        with_for_update(). \
        filter_by(question_id=question_id). \
        all()

    routing_successful = False
    sentinel_route = None
    for route in question_routes:
        if route.state == SentinelRouteState.ROUTED:
            sentinel_route = route

        if route.state == RouteState.BIDDING and timeout:
            route.state = RouteState.TIMEOUT
            route.expert_state.state = compute_expert_state(route)
        elif route.state == RouteState.BIDDING and not timeout:
            route.state = RouteState.LOST
            route.expert_state.state = compute_expert_state(route)

        if route.state == RouteState.KING:
            route.state = RouteState.WORKING
            route.expert_state.state = compute_expert_state(route)
            question_state.question.expert_id = route.expert_id
            routing_successful = True

    if not sentinel_route:
        raise Exception('Question finished routing (2)')

    assert sentinel_route.expert_id == 0

    if routing_successful:
        sentinel_route.state = SentinelRouteState.SUCCESS
    else:
        sentinel_route.state = SentinelRouteState.FAILED

    chatting_timeout = RREConfig.CHATTING_TIMEOUT

    question_state.chatting_expiration = datetime.utcnow() + timedelta(seconds=chatting_timeout)
    question_state.state = compute_question_state(question_routes)
    question_state.num_bidding = compute_num_bidding(question_routes)
    db.session.commit()

    # Todo: Temporary disable session timeout
    # if routing_successful and question_state.state != QuestionState.FAILED:
    # handle_chatting_timeout.s(question_id).apply_async(countdown=chatting_timeout)


@celery.task
def handle_question_created(question_id):
    db.session.commit()  # Fix issue related to stale data from db

    question_state = QuestionStateModel.query.get(question_id)
    assert question_state

    if question_state.state != QuestionState.NOT_ROUTED:
        raise Exception('Question already routed (1)')

    expert_states = rre.select_experts_for_question(question_state)

    sentinel_route = RouteModel(
        expert_id=0,
        question_state=question_state,
        state=SentinelRouteState.ROUTED,
    )
    db.session.add(sentinel_route)

    question_state.routing_expiration = datetime.utcnow() + timedelta(seconds=RREConfig.ROUTING_TIMEOUT)
    _route_experts_to_question(question_state, expert_states)

    db.session.commit()

    handle_route_timeout.s(question_id, timeout=True).apply_async(countdown=RREConfig.ROUTING_TIMEOUT)


@celery.task()
def handle_bid(expert_id, question_id, bid_amount):
    assert expert_id != 0

    expert_state = ExpertStateModel.query.get(expert_id)
    assert expert_state

    if expert_state.state != ExpertState.BIDDING:
        raise Exception('Expert is not bidding')

    question_routes = RouteModel.query. \
        with_for_update(). \
        filter_by(question_id=question_id). \
        all()

    state_from_routes = compute_question_state(question_routes)
    if state_from_routes not in (QuestionState.NO_KING, QuestionState.HAS_KING):
        raise Exception('Question finished routing (1)')

    question = QuestionModel.query.filter_by(id=question_id).one()

    bid_route = None
    king_route = None

    for route in question_routes:
        if (route.expert_id == expert_id) and (route.state == RouteState.BIDDING):
            bid_route = route
        if route.state == RouteState.KING:
            king_route = route

    if not bid_route:
        raise Exception('Expert has no bidding routes')

    bid_route.bid_amount = bid_amount

    rank = rre.get_expert_rank(expert_state, question.topic_id)

    grant_score = rre.calculate_winning_scores(bid_amount, rank)

    bid_route.grant_score = grant_score

    if king_route:
        assert king_route.expert_id != expert_id
        king_win = float_operator.greater_than_or_equal(king_route.grant_score, grant_score)

        if king_win:
            bid_route.state = RouteState.LOST
        else:
            king_route.state = RouteState.LOST
            bid_route.state = RouteState.KING
    else:
        bid_route.state = RouteState.KING

    bid_route.question_state.state = compute_question_state(question_routes)
    bid_route.question_state.num_bidding = compute_num_bidding(question_routes)
    bid_route.expert_state.state = compute_expert_state(bid_route)

    if king_route:
        king_route.expert_state.state = compute_expert_state(king_route)

    db.session.commit()


@celery.task()
def handle_skip(expert_id, question_id):
    assert expert_id != 0
    expert_state = ExpertStateModel.query.get(expert_id)
    assert expert_state

    if expert_state.state != ExpertState.BIDDING:
        raise Exception('Expert is not bidding')

    question_routes = RouteModel.query. \
        with_for_update(). \
        filter_by(question_id=question_id). \
        all()

    if compute_question_state(question_routes) not in (QuestionState.NO_KING, QuestionState.HAS_KING):
        raise Exception('Question finished routing')

    bid_route = None
    for route in question_routes:
        if (route.expert_id == expert_id) and (route.state == RouteState.BIDDING):
            bid_route = route
    if not bid_route:
        raise Exception('Expert has no bidding routes')

    bid_route.state = RouteState.SKIPPED
    bid_route.question_state.state = compute_question_state(question_routes)
    bid_route.question_state.num_bidding = compute_num_bidding(question_routes)
    bid_route.expert_state.state = compute_expert_state(bid_route)

    db.session.commit()


@celery.task()
def handle_question_done(question_id):
    # Get question state
    question_state = QuestionStateModel.query.get(question_id)
    assert question_state

    # Only question in working state can be marked as done
    if question_state.state != QuestionState.WORKING:
        raise Exception('Question not in working state')

    # Change state from working state to rating complete
    _change_route_state(question_state, RouteState.RATING)


@celery.task()
def handle_question_rating(question_id):
    question_state = QuestionStateModel.query.get(question_id)
    assert question_state

    if question_state.state != QuestionState.RATING:
        raise Exception('Question not in rating state (1)')

    question_routes = RouteModel.query. \
        with_for_update(). \
        filter_by(question_id=question_id). \
        all()

    rating_route = None
    for route in question_routes:
        if route.state == RouteState.RATING:
            rating_route = route
            break

    if not rating_route:
        raise Exception('Question not in rating state (2)')

    rating_route.state = RouteState.COMPLETE
    question_state.state = compute_question_state(question_routes)
    question_state.num_bidding = compute_num_bidding(question_routes)

    assert question_state.num_bidding == 0

    # Note: we don't compute_expert_state because they have already transitioned to not_routed when rating was
    # entered and we don't want to overwrite expert_state if they've already been routed to another question
    db.session.commit()
