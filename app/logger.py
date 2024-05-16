import sys

from loguru import logger

from app.env import LOG_LEVEL, DEVELOPMENT, LOG_OUTPUT

logger_args = {"level": LOG_LEVEL, "colorize": False, "serialize": False}

if DEVELOPMENT:
    logger.warning("Running in dev mode!")
    logger_args["colorize"] = True

if LOG_OUTPUT.lower() == "json":
    logger.info("Using JSON logging (colored output is disabled)")
    logger_args["serialize"] = True
    logger_args["colorize"] = False

logger.remove(0)

# Set the default value of our extra request_id
logger.configure(extra={"request_id": "00000000-0000-0000-0000-000000000000"})
logger.add(sys.stdout, **logger_args)


def get_logger() -> logger:
    return logger
