from uuid import UUID

from fastapi import APIRouter

audit_router = APIRouter(prefix="/audit", tags=["Audit"])


@audit_router.get("/tags/{tag_id}", tags=["Paginated"])
def list_the_audit_record_for_the_supplied_tag(tag_id: UUID):
    """Listing endpoint to show the complete audit record for the supplied tag"""
    ...


@audit_router.get("/users/{username}", tags=["Paginated"])
def list_the_audit_record_for_the_supplied_user(tag_id: str):
    """Listing endpoint to show the complete audit record for the supplied user"""
    ...