import uuid
from datetime import datetime

from app.logger import logger
from app.models.sequence import DocumentSequence
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
        await self.history_service.add(new_tag)

        # Make an audit log
        await self.audit_service.add(
            "create", "tag", "Creating new Tag", user=self.user.username, tag_id=new_id, version=new_tag["_version"]
        )

        return new_tag

    async def delete(self, tag_id: uuid.UUID, sequence: DocumentSequence) -> dict:
        logger.info(f"Deleting Tag [{tag_id}]")
        tag = await self.get(tag_id, sequence=sequence)
        now = datetime.utcnow()
        tag["_source"]["deleted"] = now
        tag["_source"]["updated"] = now

        deleted = await self._index(doc_id=tag_id, body=tag["_source"], sequence=sequence)
        await self.history_service.add(deleted)

        await self.audit_service.add(
            "delete",
            "tag",
            f"Tag [{tag['_source']['name']}] deleted",
            user=self.user.username,
            tag_id=tag["_id"],
            version=deleted["_version"],
        )
