from flask import request
from marshmallow import fields, Schema
from functools import wraps

from main.enums import AccountType
from main.libs import jwttoken
from main.models.user import UserModel
from main.models.admin import AdminModel
from main.models.expert import ExpertModel
from main import errors


AudienceModels = {
    AccountType.USER: UserModel,
    AccountType.EXPERT: ExpertModel,
    AccountType.ADMIN: AdminModel,
}


def get_audience_account(audience):
    authorization = None

    if 'Authorization' in request.headers:
        authorization = request.headers['Authorization']

    if not authorization:
        return None

    if not authorization.startswith('Bearer '):
        return None

    token = jwttoken.decode(authorization[len('Bearer '):], audience)
    if not token:
        return None
    account = AudienceModels[audience].query.get(token['sub'])
    if not account:
        return None
    if account.access_token_nonce != token['nonce']:
        return None
    return account


class GoogleAuthSchema(Schema):
    id_token = fields.String(required=True)
    access_token = fields.String(required=True)


def requires_token_auth(audience):
    def requires_token_auth_decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            account = get_audience_account(audience)
            if not account:
                raise errors.Unauthorized()
            kwargs[audience] = account
            return f(*args, **kwargs)

        return decorated_function

    return requires_token_auth_decorator
