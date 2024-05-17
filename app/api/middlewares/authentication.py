from fastapi import FastAPI, Request, Response

from app.logger import logger
from app.models.user import User


def attach_user_authentication(app: FastAPI):
    logger.debug("Attaching user authentication middleware to app")

    # TODO: Handle user authentication here. Get user details from somewhere and attach the user Object into state

    @app.middleware("http")
    async def add_user_to_request(request: Request, call_next) -> Response:

        request.state.user = User(username="Demo User", roles=["admin"])
        return await call_next(request)
