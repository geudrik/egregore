from fastapi import APIRouter

metrics_router = APIRouter(prefix="/metrics", tags=["Metrics"])


# TODO: Most of these routes should likely be cached to avoid undue burden on the cluster


@metrics_router.get("/tags")
async def get_tag_metrics():
    """Return a dict of metrics around total tags, number recent edits, etc"""
    ...


@metrics_router.get("/audit")
async def get_audit_metrics():
    """Returns a dict of metrics around number of actions occurring within the system, what kinds of things are
    happening, etc
    """
    ...
