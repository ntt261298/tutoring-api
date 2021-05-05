from marshmallow import fields, Schema

from config import config
from main.schemas.base import BaseSchema


class _FileSchema(Schema):
    id = fields.Integer()
    rendered_data = fields.String()
    name = fields.String()


class _StateQuestionSchema(Schema):
    id = fields.Integer()
    text = fields.String()
    created = fields.DateTime()
    user_id = fields.Integer()
    topic_id = fields.Integer()
    topic_name = fields.String()
    file = fields.Nested(_FileSchema)


class ExpertStateSchema(BaseSchema):
    expert_id = fields.Integer()
    state = fields.String()
    pre_state = fields.String()
    connected = fields.Boolean()
    question_info = fields.Nested(_StateQuestionSchema)
    timestamp = fields.Integer()
    updated = fields.Integer()
    routing_timeout = fields.Integer()
    chatting_timeout = fields.Integer()
    remain_claim_time = fields.Integer()
    remain_chatting_time = fields.Integer()
    fixed_bid_amount = fields.Float(default=config.FIXED_BID_AMOUNT)


class UserStateSchema(BaseSchema):
    user_id = fields.Integer()
    state = fields.String()
    pre_state = fields.String()
    question = fields.Nested(_StateQuestionSchema)
    timestamp = fields.Integer()
    chatting_timeout = fields.Integer()
    remain_chatting_time = fields.Integer()
