from app.logger import logger
from app.service.base import BaseService


class TagHistoryService(BaseService):

    _index_name = "tags-history"

    async def add(self, body: dict) -> None:
        logger.info("Adding new Tag history entry", tag_id=body["id"], tag_version=body["version"])
        await self._index(body=body)
