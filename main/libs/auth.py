from functools import wraps

from flask import request

from main import errors
from main.libs.jwttoken import decode


def requires_token_auth(audience):
    def requires_token_auth_with_decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            authorization = None

            if 'Authorization' in request.headers:
                authorization = request.headers['Authorization']
                print("authorization", authorization)

            if not authorization:
                return None

            if not authorization.startswith('Bearer '):
                return None

            token = decode(authorization[len('Bearer '):], audience)

            print('token', token)

            return f(*args, **kwargs)

        return decorated_function
    return requires_token_auth_with_decorator
