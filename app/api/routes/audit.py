from uuid import UUID

from fastapi import APIRouter, Depends

from app.models.pagination import PaginatedTagHistoryList, SortingArgs, FilteringArgs, PaginationArgs
from app.models.tag import TagHistory
from app.service.factory import get_tag_history_service
from app.service.tag_history import TagHistoryService

audit_router = APIRouter(prefix="/audit", tags=["Audit"])


@audit_router.get("/tags/{tag_id}", tags=["Paginated"])
async def list_the_audit_record_for_the_supplied_tag(
    tag_id: UUID,
    history_service: TagHistoryService = Depends(get_tag_history_service),
    pagination=Depends(PaginationArgs),
    filtering=Depends(FilteringArgs),
    sorting=Depends(SortingArgs),
) -> PaginatedTagHistoryList:
    query = {"term": {"id": str(tag_id)}}
    count, limit, offset, res = await history_service.list(
        pagination, filtering, sorting, filter_deleted=False, extra_filter=query
    )
    ret = [TagHistory(**i["_source"]) for i in res]
    return PaginatedTagHistoryList(limit=limit, offset=offset, total=count, items=ret)


@audit_router.get("/users/{username}", tags=["Paginated"])
async def list_the_audit_record_for_the_supplied_user(tag_id: str):
    """Listing endpoint to show the complete audit record for the supplied user"""
    ...
