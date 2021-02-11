class StatusCode:
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403


class ErrorCode:
    BAD_REQUEST = 40000
    VALIDATION_ERROR = 40001
    PERMISSION_DENIED = 40003


class BadRequest(Exception):
    status_code = StatusCode.BAD_REQUEST
    error_code = ErrorCode.BAD_REQUEST
    error_message = "Bad request"


class PermissionDenied(Exception):
    status_code = StatusCode.FORBIDDEN
    error_code = ErrorCode.PERMISSION_DENIED
    error_message = "Permission Denied"
