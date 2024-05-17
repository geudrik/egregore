from fastapi import Request

from app.lib.exceptions import ServerError
from app.lib.opensearch import client
from app.service.audit import AuditService
from app.service.tag import TagService
from app.service.tag_history import TagHistoryService


def get_tag_service(request: Request) -> TagService:
    """Dependable to get an instance of the Tag service"""
    if not getattr(request.state, "user", False):
        raise ServerError("User object missing from request")
    return TagService(request.state.user, client, TagHistoryService(client), AuditService(client))