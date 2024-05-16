import time
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from starlette.responses import JSONResponse

from app.logger import get_logger

logger = get_logger()


def attach_request_logging(app: FastAPI):
    logger.debug("Attaching request logging to root app")

    @app.middleware("http")
    async def log_requests(request: Request, call_next) -> Response:
        request_id = str(uuid4())
        start_time = time.time()
        with logger.contextualize(request_id=request_id):
            try:
                response = await call_next(request)

            except Exception as e:
                logger.exception(f"Request failed: {e}")
                response = JSONResponse(content={"success": False}, status_code=500)

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
                    }
                ).info(
                    f"{request.method} {request.url.path} -> [{response.status_code}] in {formatted_process_time}ms",
                    duration=formatted_process_time,
                )
                return response
