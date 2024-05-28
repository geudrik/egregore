from uuid import UUID

from fastapi import APIRouter, Depends

from app.models.audit import Audit
from app.models.pagination import SortingArgs, FilteringArgs, PaginationArgs, PaginatedAuditList
from app.service.audit import AuditService
from app.service.factory import get_audit_service

audit_router = APIRouter(prefix="/audit", tags=["Audit"])


@audit_router.get("/tags/{tag_id}", tags=["Paginated"])
async def list_the_audit_record_for_the_supplied_tag(
    tag_id: UUID,
    audit_service: AuditService = Depends(get_audit_service),
    pagination=Depends(PaginationArgs),
    filtering=Depends(FilteringArgs),
    sorting=Depends(SortingArgs),
) -> PaginatedAuditList:
    query = {"term": {"tag_id": str(tag_id)}}
    limit, offset, res = await audit_service.list(pagination, filtering, sorting, extra_filter=query)
    count = await audit_service.count({"query": {"bool": {"filter": query}}})
    ret = [Audit(**i["_source"]) for i in res]
    return PaginatedAuditList(limit=limit, offset=offset, total=count, items=ret)


@audit_router.get("/users/{username}", tags=["Paginated"])
async def list_the_audit_record_for_the_supplied_user(
    username: str,
    audit_service: AuditService = Depends(get_audit_service),
    pagination=Depends(PaginationArgs),
    filtering=Depends(FilteringArgs),
    sorting=Depends(SortingArgs),
) -> PaginatedAuditList:
    query = {"term": {"user": username}}
    limit, offset, res = await audit_service.list(pagination, filtering, sorting, extra_filter=query)
    count = await audit_service.count({"query": {"bool": {"filter": query}}})
    ret = [Audit(**i["_source"]) for i in res]
    return PaginatedAuditList(limit=limit, offset=offset, total=count, items=ret)
