import time
from datetime import datetime

from sqlalchemy.orm import contains_eager

from main.enums import ExpertState, RREConfig, QuestionState
from main.models.expert import ExpertModel
from main.models.user import UserModel
from main.models.question import QuestionModel
from main.models.expert_state import ExpertStateModel


def _get_remain_claim_time(expert, current_question):
    remain_claim_time = RREConfig.ROUTING_TIMEOUT
    if expert and expert.expert_state.state in [ExpertState.BIDDING, ExpertState.KING]:
        remain_claim_time = current_question.question_state.routing_expiration - datetime.utcnow()
        remain_claim_time = remain_claim_time.total_seconds()
        if remain_claim_time <= 0:
            remain_claim_time = 0

    return remain_claim_time


def _get_remain_chatting_time(current_question):
    remain_chatting_time = 0
    if current_question and current_question.question_state.state == QuestionState.WORKING:
        remain_chatting_time = current_question.question_state.chatting_expiration - datetime.utcnow()
        remain_chatting_time = remain_chatting_time.total_seconds()
        if remain_chatting_time < 0:
            remain_chatting_time = 0

    return remain_chatting_time


def generate_expert_state(expert_id):
    expert = ExpertModel.query. \
        join(ExpertModel.expert_state). \
        outerjoin(ExpertStateModel.current_question). \
        filter(ExpertModel.id == expert_id). \
        options(
            contains_eager(ExpertModel.expert_state).
            contains_eager(ExpertStateModel.current_question)
        ). \
        one()

    current_question = None
    pre_state = None

    if expert.expert_state.state != ExpertState.NOT_ROUTED:
        current_question = expert.expert_state.current_question

    data = {
        'expert_id': expert.id,
        'state': expert.expert_state.state,
        'pre_state': pre_state,
        'connected': expert.expert_state.connected,
        'question_info': current_question,
        'timestamp': time.time() * 1000,
        'routing_timeout': RREConfig.ROUTING_TIMEOUT if current_question else 0,
        'chatting_timeout': RREConfig.CHATTING_TIMEOUT if current_question else 0,
        'remain_claim_time': _get_remain_claim_time(expert, current_question),
        'remain_chatting_time': _get_remain_chatting_time(current_question),
    }

    return data


def generate_user_state(user_id):
    user = UserModel.query. \
        join(UserModel.current_question). \
        join(QuestionModel.question_state). \
        filter(UserModel.id == user_id). \
        options(
            contains_eager(UserModel.current_question)). \
        options(
            contains_eager(UserModel.current_question).
            contains_eager(QuestionModel.question_state)). \
        one_or_none()

    current_question = user.current_question if user else None

    pre_state = None

    if current_question:
        state = current_question.question_state.state
        if state in QuestionState.get_finished_states():
            # If state is one of the final states, store the final state before reset the state to null
            pre_state = state
            current_question = None

    return {
        'user_id': user_id,
        'state': current_question.question_state.state if current_question else None,
        'pre_state': pre_state,
        'question': current_question,
        'timestamp': time.time() * 1000,
        'chatting_timeout': RREConfig.CHATTING_TIMEOUT if current_question else 0,
        'remain_chatting_time': _get_remain_chatting_time(current_question),
    }
