from flask import jsonify
from marshmallow import fields, Schema

from main import app


class Error(Exception):
    def __init__(self, error_data=None):
        super(Error)
        self.error_data = error_data or {}

    def to_response(self):
        print('Go in here')
        resp = jsonify(ErrorSchema().dump(self))
        resp.status_code = self.status_code
        return resp


class ErrorSchema(Schema):
    error_code = fields.Int()
    error_message = fields.String()
    error_data = fields.Raw()


class StatusCode:
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403


class ErrorCode:
    BAD_REQUEST = 40000
    VALIDATION_ERROR = 40001
    PERMISSION_DENIED = 40003
    USER_EMAIL_ALREADY_EXISTED = 40032
    USER_ERROR = 40033
    UNAUTHORIZED = 40100


class BadRequest(Error):
    status_code = StatusCode.BAD_REQUEST
    error_code = ErrorCode.BAD_REQUEST
    error_message = "Bad request"


class PermissionDenied(Error):
    status_code = StatusCode.FORBIDDEN
    error_code = ErrorCode.PERMISSION_DENIED
    error_message = "Permission Denied"


class AccountNotExisted(Error):
    status_code = StatusCode.BAD_REQUEST
    error_code = ErrorCode.BAD_REQUEST
    error_message = "The account you've entered doesn't exist."


class EmailAndPasswordNotMatch(Error):
    status_code = StatusCode.BAD_REQUEST
    error_code = ErrorCode.BAD_REQUEST
    error_message = "Invalid email or password."


class UserEmailAlreadyExistedError(Error):
    status_code = StatusCode.BAD_REQUEST
    error_code = ErrorCode.USER_EMAIL_ALREADY_EXISTED
    error_message = 'This email is already registered. Click here to login.'


class Unauthorized(Error):
    status_code = StatusCode.UNAUTHORIZED
    error_code = ErrorCode.UNAUTHORIZED
    error_message = 'Unauthorized'


class UserError(Error):
    status_code = StatusCode.BAD_REQUEST
    error_code = ErrorCode.USER_ERROR
    error_message = 'Client app fault'

    def __init__(self, code=ErrorCode.USER_ERROR, message='User fault', data=None):
        super(self.__class__, self).__init__(data)
        self.error_code = code
        self.error_message = message


class UserErrors:
    NICKNAME_LENGTH_LIMIT = 'Nickname must be at least 6 characters in length.'
    UNAVAILABLE_NICKNAME = 'Nickname is not available. Please choose another one.'
    INVALID_CURRENT_PASSWORD = 'Invalid current password.'
    PASSWORD_CONTAIN_SPECIAL_CHARACTERS = 'Password must not contain special characters.'


@app.errorhandler(Error)
def error_handler(error):
    return error.to_response()
