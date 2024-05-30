import time
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from starlette.responses import JSONResponse

from app.lib.exceptions import APIException, ServerError
from app.logger import get_logger

logger = get_logger()


def attach_request_logging(app: FastAPI):
    logger.debug("Attaching request logging middleware to app")

    @app.middleware("http")
    async def log_requests(request: Request, call_next) -> Response:
        request_id = str(uuid4())
        start_time = time.time()
        with logger.contextualize(request_id=request_id):
            try:
                response = await call_next(request)

            except Exception as e:

                response = {
                    "requestID": request_id,
                    "success": False,
                    "details": {
                        "statusCode": 500,
                        "errorCode": ServerError.error_code,
                        "errorMessage": "Internal Server Error",
                        "errorDetails": "",
                    },
                }

                match e:

                    case APIException():
                        if isinstance(e, ServerError):
                            logger.exception("API Server Error Thrown")

                        response["details"]["statusCode"] = e.status_code
                        response["details"]["errorCode"] = e.error_code
                        response["details"]["errorMessage"] = e.error_message
                        response["details"]["errorDetails"] = e.exception_message

                    case Exception():
                        logger.exception(f"Request failed due to unhandled exception: {e}")

                response = JSONResponse(content=response, status_code=response["details"]["statusCode"])

            finally:
                process_time = (time.time() - start_time) * 1000
                formatted_process_time = "{0:.2f}".format(process_time)
                response.headers["X-Request-ID"] = request_id
                logger.bind(
                    **{
                        "method": request.method,
                        "path": request.url.path,
                        "raw_path": (
                            (request.scope["root_path"] + request.scope["route"].path)
                            if request.scope.get("route")
                            else request.url.path
                        ),
                        "code": response.status_code,
                        "duration": formatted_process_time,
                        "username": None,
                    }
                ).info(
                    f"{request.method} {request.url.path} -> [{response.status_code}] in {formatted_process_time}ms",
                    duration=formatted_process_time,
                )
                return response
