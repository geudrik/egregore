import uuid
from datetime import datetime

from app.logger import logger
from app.service.audit import AuditService
from app.service.base import BaseService
from app.service.tag_history import TagHistoryService


class TagService(BaseService):

    _index_name = "tags-latest"

    def __init__(self, user, client, history_service: TagHistoryService, audit_service: AuditService):
        self.user = user
        self.client = client
        self.history_service = history_service
        self.audit_service = audit_service

    async def create(self, tag_data: dict) -> dict:
        new_id = uuid.uuid4()
        now = datetime.utcnow()
        tag_data["author"] = self.user.username
        tag_data["editor"] = self.user.username
        tag_data["created"] = now
        tag_data["updated"] = now
        logger.info(f"Creating new Tag [{tag_data['name']}]", tag_id=new_id)
        new_tag = await self._index(tag_data, doc_id=new_id)

        # Add this newly created tag to our history
        history_body: dict = new_tag["_source"]
        history_body["version"] = new_tag["_version"]
        history_body["id"] = new_tag["_id"]
        logger.info(f"Adding newly created tag to history", tag_id=new_id)
        await self.history_service.add(history_body)

        # Make an audit log
        await self.audit_service.add(
            "create",
            "tag",
            self.user.username,
            f"New tag [{tag_data['name']}] created",
            tag_id=new_id,
        )

        return new_tag
