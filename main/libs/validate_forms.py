from functools import wraps

from flask import request
from marshmallow import ValidationError

from main import errors


def validate_forms(schema):
    def parse_request_form_with_decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            request_args = request.form.to_dict()
            try:
                parsed_args = schema.load(request_args)
            except ValidationError as err:
                raise errors.BadRequest(err)

            kwargs['args'] = parsed_args
            return f(*args, **kwargs)

        return decorated_function

    return parse_request_form_with_decorator
