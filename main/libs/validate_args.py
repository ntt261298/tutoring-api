from functools import wraps

from flask import request
from marshmallow import ValidationError

from main import errors


def validate_args(schema):
    def validate_args_with_decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            request_args = request.get_json() or {}
            try:
                result = schema.load(request_args)
            except ValidationError as err:
                raise errors.BadRequest(err)

            kwargs['args'] = result
            return f(*args, **kwargs)

        return decorated_function
    return validate_args_with_decorator
