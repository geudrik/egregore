from uuid import UUID

from app.logger import logger
from app.service.base import BaseService


class AuditService(BaseService):

    _index_name = "tags-audit"

    async def add(
        self,
        action: str,
        component: str,
        message: str,
        user: str,
        subcomponent: str = None,
        tag_id: UUID = None,
        version: int = None,
    ) -> None:
        """Create a new Audit entry
        :arg action: Action to perform
        :arg component: The component the action is being performed on (tag, tag history, audit, comment, etc)
        :arg user: The user that's performing this action
        :arg message: A message describing what's going on and/or why
        :arg subcomponent: Optional, a secondary component that's having action taken against (eg:
        :arg tag_id: Optional, the ID of a Tag if available
        :arg version: Optional, the version of the Tag if available
        """
        body = {
            "action": action,
            "component": component,
            "user": user,
            "message": message,
            "subcomponent": subcomponent,
            "tag_id": tag_id,
            "version": version,
        }
        logger.info("Adding new Audit entry", **body)
        await self._index(body=body)
