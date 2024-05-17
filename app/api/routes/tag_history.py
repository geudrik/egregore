from uuid import UUID

from fastapi import APIRouter

tag_history_router = APIRouter(prefix="/tags/history", tags=["Tag History"])


@tag_history_router.get("/{tag_id}", tags=["Paginated"])
def list_all_historical_changes_for_a_tag(tag_id: UUID): ...
