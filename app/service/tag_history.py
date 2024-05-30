from app.logger import logger
from app.service.base import BaseService


class TagHistoryService(BaseService):

    _index_name = "tags-history"

    async def add(self, doc: dict) -> None:
        """Add the supplied doc to the history index
        :arg body The whole doc body returned from an index operation (including the _ fields)
        """
        history_body = doc["_source"].copy()  # Need to copy this as this is a mutable object
        history_body["version"] = doc["_version"]
        history_body["id"] = doc["_id"]

        logger.debug("Adding changes to Tag to history", tag_id=history_body["id"], tag_version=history_body["version"])
        await self._index(body=history_body)
