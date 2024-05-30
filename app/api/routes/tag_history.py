from uuid import UUID

from fastapi import APIRouter, Depends

from app.models.pagination import PaginationArgs, FilteringArgs, SortingArgs, PaginatedTagHistoryList
from app.models.tag import TagHistory
from app.service.factory import get_tag_history_service
from app.service.tag_history import TagHistoryService

tag_history_router = APIRouter(prefix="/tags/history", tags=["Tag History"])


@tag_history_router.get("/{tag_id}", tags=["Paginated"])
async def list_all_historical_changes_for_a_tag(
    tag_id: UUID,
    history_service: TagHistoryService = Depends(get_tag_history_service),
    pagination=Depends(PaginationArgs),
    filtering=Depends(FilteringArgs),
    sorting=Depends(SortingArgs),
) -> PaginatedTagHistoryList:
    query = {"term": {"id": str(tag_id)}}
    res = await history_service.list(
        pagination, filtering, sorting, extra_filter=query
    )
    ret = [TagHistory(**i["_source"]) for i in res.data]
    return PaginatedTagHistoryList(limit=res.limit, offset=res.offset, total=res.total, items=ret)
