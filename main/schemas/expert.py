from marshmallow import fields

from main.schemas.base import BaseSchema


class ExpertSchema(BaseSchema):
    id = fields.Integer()
    email = fields.Email()
    nickname = fields.String()
    payment_method = fields.String()
    account_type = fields.String()
