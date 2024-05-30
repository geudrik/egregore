from fastapi import APIRouter, Depends

from app.service.audit import AuditService
from app.service.factory import get_tag_service, get_audit_service
from app.service.tag import TagService

metrics_router = APIRouter(prefix="/metrics", tags=["Metrics"])


# TODO: Most of these routes should likely be cached to avoid undue burden on the cluster


@metrics_router.get("/tags")
async def get_tag_metrics(tag_service: TagService = Depends(get_tag_service)):
    """Return a dict of metrics around total tags, number recent edits, etc"""
    clauses = await tag_service.count_clauses()
    patterns = await tag_service.count_patterns()
    total_tags_including_deleted = await tag_service.count(include_deleted=True)
    tag_count_excluding_deleted = await tag_service.count()
    return (
        clauses
        | patterns
        | {
            "tags": {
                "count": total_tags_including_deleted,
                "deleted": total_tags_including_deleted - tag_count_excluding_deleted,
                "published": "TODO",
            },
        }
    )


@metrics_router.get("/audit")
async def get_audit_metrics(audit_service: AuditService = Depends(get_audit_service)):
    """Returns a dict of metrics around number of actions occurring within the system, what kinds of things are
    happening, etc
    """
    return await audit_service.metrics()
