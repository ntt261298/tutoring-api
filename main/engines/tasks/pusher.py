from celery.utils.log import get_task_logger

from main import celery
from main.engines import pusher
from main.engines.state_machine import generate_user_state, generate_expert_state
from main.schemas.state import UserStateSchema, ExpertStateSchema

logger = get_task_logger(__name__)


@celery.task()
def push_user_state(user_id):
    user_state = generate_user_state(user_id)
    print('user_state', user_state)
    pusher.trigger_state_change(
        'user',
        user_id,
        UserStateSchema().dump(user_state)
    )


@celery.task()
def push_expert_state(expert_id):
    expert_state = generate_expert_state(expert_id)
    pusher.trigger_state_change(
        'expert',
        expert_id,
        ExpertStateSchema().dump(expert_state))
