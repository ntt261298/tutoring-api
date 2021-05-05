from sqlalchemy.orm import contains_eager

from main.enums import ExpertState
from main.models.expert_state import ExpertStateModel
from main.models.route import RouteModel
from main.models.expert_topic import ExpertTopicModel
from main.models.expert_rank import ExpertRankModel


WEIGHT_RANK = 0.5
WEIGHT_BID = 0.5
MAX_BID = 16
MAX_RANK = 5


def select_experts_for_question(question_state):
    routes_subq = RouteModel.query.filter(RouteModel.question_id == question_state.question_id).subquery()
    # First join + filter gets the experts who have match the question's topic
    # Second join + filter gets the experts who don't already have a route for this problem
    # We take some large number ordered randomly
    # Note: this is using optimistic locking. If it starts to fail a lot, might want to use with_for_update for
    # pessimistic locking instead or do bucketing after excluding experts after locking routes

    experts_states = ExpertStateModel.query. \
        join(ExpertStateModel.expert_topics). \
        filter(ExpertTopicModel.topic_id == question_state.topic_id). \
        join(ExpertStateModel.expert_ranks). \
        filter(ExpertRankModel.topic_id == question_state.topic_id). \
        options(contains_eager(ExpertStateModel.expert_ranks)). \
        outerjoin(routes_subq, ExpertStateModel.expert_id == routes_subq.c.expert_id). \
        filter(routes_subq.c.expert_id.is_(None)). \
        filter(ExpertStateModel.connected.is_(True)). \
        filter(ExpertStateModel.state == ExpertState.NOT_ROUTED)

    experts_states = experts_states.all()

    return experts_states


# Granting score calculation
# 0 < grant score < 1
def calculate_winning_scores(bid, rank):
    grant_score = WEIGHT_RANK * (rank / MAX_RANK) + WEIGHT_BID * ((MAX_BID - bid) / MAX_BID)
    return grant_score


def get_expert_rank(expert_state, topic_id):
    current_rank = 0
    for rank in expert_state.expert_ranks:
        if rank.topic_id == topic_id:
            current_rank = rank.score_avg

    return current_rank
