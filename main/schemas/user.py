from marshmallow import fields

from main.schemas.base import BaseSchema


class AccessTokenSchema(BaseSchema):
    access_token = fields.String()
    account_id = fields.Integer()
    account_type = fields.String()
    auth_type = fields.String()
    nickname = fields.String()
    is_signup = fields.Boolean()
    email = fields.String()


class UserSchema(BaseSchema):
    id = fields.Integer()
    google_id = fields.String()
    email = fields.Email()
    nickname = fields.String()
    free_credit_balance = fields.Integer()
    paid_credit_balance = fields.Integer()


class UserSubscriptionPackageSchema(BaseSchema):
    package_name = fields.String()
    package_type = fields.String()
    amount = fields.Float()
    expired_in = fields.DateTime()
    status = fields.String()
