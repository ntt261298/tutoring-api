from marshmallow import fields, Schema

from config import config
from main.schemas.base import BaseSchema


class _StateQuestionSchema(Schema):
    id = fields.Integer()
    text = fields.String()
    created = fields.DateTime()
    user_id = fields.Integer()
    topic_id = fields.Integer()
    topic_name = fields.String()

    # For info message at beginning of chat session
    original_file_type = fields.String()
    original_file_url = fields.String()


class ExpertStateSchema(BaseSchema):
    class _StateParticipantSchema(Schema):
        name = fields.String()
        user_id = fields.Integer()
        expert_id = fields.Integer()

    expert_id = fields.Integer()
    state = fields.String()
    pre_state = fields.String()
    connected = fields.Boolean()
    question_info = fields.Nested(_StateQuestionSchema)
    participants = fields.Nested(_StateParticipantSchema, many=True)
    timestamp = fields.Integer()
    updated = fields.Integer()
    routing_timeout = fields.Integer()
    chatting_timeout = fields.Integer()
    remain_claim_time = fields.Integer()
    remain_chatting_time = fields.Integer()
    fixed_bid_amount = fields.Float(default=config.FIXED_BID_AMOUNT)
