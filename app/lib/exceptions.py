ERROR_CODES = {
    10000: "The server encountered an unexpected error. Your request was cancelled",
    10001: "The request you made could not be fulfilled as the path wasn't found",
    10002: "The request supplied was malformed in some way",
    10003: "Unable to perform the request due to a conflict",
    10004: "Unable to perform the request due to an integrity error",
    10011: "Header parameter X-API-Key is missing from the headers of the request",
    10012: "Supplied API is malformed",
    10013: "You do not have permission to access the requested resource",
    10014: "Invalid token",
}


class APIException(Exception):

    # The default status code returned on the API
    status_code = 500

    # The default error message code
    error_code = 10000

    @property
    def error_message(self):
        return ERROR_CODES.get(self.error_code, "Unknown Error")

    @property
    def exception_message(self):
        args = getattr(self, "args", "")
        message = args[0] if args else ""
        return message


class ServerError(APIException):
    pass


class BadRequest(APIException):
    status_code = 400
    error_code = 10002


class ClientError(BadRequest):
    pass


class Unauthorized(APIException):
    status_code = 401
    error_code = 10011


class MalformedAPIKey(APIException):
    status_code = 401
    error_code = 10012


class Forbidden(APIException):
    status_code = 403
    error_code = 10013


class NotFound(APIException):
    status_code = 404
    error_code = 10001


class Conflict(APIException):
    status_code = 409
    error_code = 10003


class IntegrityError(APIException):
    status_code = 409
    error_code = 10004
