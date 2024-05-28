ERROR_CODES = {
    "sploot": "The server encountered an unexpected error",
    "goldfish": "The request you made could not be fulfilled as something wasn't found",
    "shoebill": "The request supplied was malformed in some way",
    "poodle moth": "Unable to perform the request due to a conflict",
    "narwhal": "Unable to perform the request due to an integrity error",
    "aye-aye": "Header parameter X-API-Key is missing from the headers of the request",
    "markhor": "Supplied API Key is malformed",
    "platypus": "You do not have permission to access the requested resource",
}


class APIException(Exception):

    # The default status code returned on the API
    status_code = 500

    # The default error message code
    error_code = "sploot"

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
    error_code = "shoebill"


class ClientError(BadRequest):
    pass


class Unauthorized(APIException):
    status_code = 401
    error_code = "aye-aye"


class MalformedAPIKey(APIException):
    status_code = 401
    error_code = "markhor"


class Forbidden(APIException):
    status_code = 403
    error_code = "platypus"


class NotFound(APIException):
    status_code = 404
    error_code = "goldfish"


class Conflict(APIException):
    status_code = 409
    error_code = "poodle moth"


class IntegrityError(APIException):
    status_code = 409
    error_code = "narwhal"
