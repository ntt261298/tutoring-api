from celery.utils.log import get_task_logger
from marshmallow import fields

from main import celery
from main.schemas.base import BaseSchema
from main.engines import pusher
from main.engines.state_machine import generate_user_state, generate_expert_state

logger = get_task_logger(__name__)


class _StateQuestionSchema(BaseSchema):
    id = fields.Integer(allow_none=True)


class ExpertPusherStateSchema(BaseSchema):
    state = fields.String()
    pre_state = fields.String()


class UserPusherStateSchema(BaseSchema):
    state = fields.String()
    pre_state = fields.String()
    question = fields.Nested(_StateQuestionSchema, allow_none=True)


@celery.task()
def push_user_state(user_id):
    user_state = generate_user_state(user_id)
    pusher.trigger_state_change(
        'user',
        user_id,
        UserPusherStateSchema().dump(user_state).data
    )


@celery.task()
def push_expert_state(expert_id):
    expert_state = generate_expert_state(expert_id)
    pusher.trigger_state_change(
        'expert',
        expert_id,
        ExpertPusherStateSchema().dump(expert_state).data
    )
