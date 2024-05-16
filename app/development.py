from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.env import CYCLE_INDEX_TEMPLATES, PURGE_INDEXES_ON_SHUTDOWN
from app.infra.manager import Manager
from app.lib.opensearch import client
from app.logger import logger

""" This file defines a context manger that FAPI uses during start/shutdown. If you set the """


@asynccontextmanager
async def lifecycle_manager(app: FastAPI):
    logger.debug("Starting index manager with app lifecycle")
    manager = Manager(client, logger)
    if CYCLE_INDEX_TEMPLATES:

        # Create all of our index templates
        await manager.create_component_templates()
        await manager.create_templates()

        # Since this is a context manager, this yield is where the rest of the app runs
        yield

        if PURGE_INDEXES_ON_SHUTDOWN:
            # Nuke all the indexes we created
            logger.warning("Purging indexes on shutdown")
            await manager.nuke()
        else:
            logger.info("Deleting all component and index templates")
            await manager.delete_templates()
            await manager.delete_component_templates()

    else:
        yield
