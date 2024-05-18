from uuid import UUID

from fastapi import APIRouter

audit_router = APIRouter(prefix="/audit", tags=["Audit"])


@audit_router.get("/tags/{tag_id}", tags=["Paginated"])
async def list_the_audit_record_for_the_supplied_tag(tag_id: UUID): ...


@audit_router.get("/users/{username}", tags=["Paginated"])
async def list_the_audit_record_for_the_supplied_user(tag_id: str):
    """Listing endpoint to show the complete audit record for the supplied user"""
    ...
