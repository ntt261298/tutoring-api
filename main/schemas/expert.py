from marshmallow import fields

from main.schemas.base import BaseSchema


class ExpertEarningSchema(BaseSchema):
    amount = fields.Float()


class ExpertRankSchema(BaseSchema):
    topic_id = fields.Integer()
    score_avg = fields.Float()


class ExpertSchema(BaseSchema):
    id = fields.Integer()
    email = fields.Email()
    nickname = fields.String()
    payment_method = fields.String()
    account_type = fields.String()
    expert_earnings = fields.Nested(ExpertEarningSchema, many=True)
    expert_ranks = fields.Nested(ExpertRankSchema, many=True)
