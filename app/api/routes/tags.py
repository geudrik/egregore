from uuid import UUID

from fastapi import APIRouter, Depends
from starlette.responses import RedirectResponse

from app.lib.sequence import get_sequence
from app.models.pagination import PaginationArgs, FilteringArgs, SortingArgs, PaginatedTagList
from app.models.sequence import DocumentSequence
from app.models.tag import Create, Tag
from app.models.tag import Pattern
from app.models.tag import Reference
from app.models.tag import Update
from app.service.factory import get_tag_service
from app.service.tag import TagService

tags_router = APIRouter(prefix="/tags", tags=["Tags"])


@tags_router.get("/", tags=["Paginated"])
async def list_all_tags(
    tag_service: TagService = Depends(get_tag_service),
    include_deleted: bool = False,
    pagination=Depends(PaginationArgs),
    filtering=Depends(FilteringArgs),
    sorting=Depends(SortingArgs),
) -> PaginatedTagList:
    count, limit, offset, res = await tag_service.list(pagination, filtering, sorting, include_deleted=include_deleted)
    # Convert list of docs into Tag instances for return in our PaginatedTagList model
    ret = [Tag(i) for i in res]

    return PaginatedTagList(limit=limit, offset=offset, total=count, items=ret)


@tags_router.get("/{tag_id}")
async def get_a_tag_by_id(
    tag_id: UUID,
    tag_service: TagService = Depends(get_tag_service),
    include_deleted: bool = False,
) -> Tag:
    """Retrieve a single Tag by its' ID"""
    doc = await tag_service.get(tag_id, allow_deleted=include_deleted)
    return Tag(doc)


@tags_router.post("/")
async def create_a_new_tag(
    new_tag: Create,
    tag_service: TagService = Depends(get_tag_service),
) -> Tag:
    ret = await tag_service.create(new_tag.model_dump())
    return Tag(ret)


@tags_router.patch("/{tag_id}")
async def update_an_existing_tag(
    tag_id: UUID,
    payload: Update,
    tag_service: TagService = Depends(get_tag_service),
    sequence: DocumentSequence = Depends(get_sequence),
) -> Tag:
    # We need to use exclude_unset here as all fields are optional. Missing fields otherwise get the default assigned
    #   value from the model, but we wan't _nothing_, since under the hood we're doing a dict merge from existing
    ret = await tag_service.update(tag_id, sequence, payload.model_dump(exclude_unset=True))
    return Tag(ret)


@tags_router.delete("/{tag_id}")
async def delete_a_tag(
    tag_id: UUID, sequence: DocumentSequence = Depends(get_sequence), tag_service: TagService = Depends(get_tag_service)
) -> None:
    """Performs a soft-deletion of the supplied tag, provided that the supplied sequence passes validation"""
    await tag_service.delete(tag_id, sequence)


@tags_router.get("/{tag_id}/comments", tags=["Comments", "Paginated"])
async def list_all_comments_for_a_tag(tag_id: UUID):
    return RedirectResponse(url=f"/comments/tags/{tag_id}", status_code=301)


@tags_router.post("/{tag_id}/comments")
async def add_a_comment_to_a_tag(tag_id: UUID):
    return RedirectResponse(url=f"/comments/tags/{tag_id}", status_code=301)


@tags_router.delete("/{tag_id}/comments/{comment_id}")
async def delete_a_comment_from_a_tag(tag_id: UUID, comment_id: UUID):
    return RedirectResponse(url=f"/comments/{comment_id}", status_code=301)


@tags_router.put("/{tag_id}/comments/{comment_id}")
async def update_a_comment_for_the_supplied_tag(tag_id: UUID, comment_id: UUID) -> RedirectResponse:
    return RedirectResponse(url=f"/comments/{comment_id}", status_code=301)


@tags_router.post("/{tag_id}/references")
async def add_a_new_reference(
    tag_id: UUID,
    payload: Reference,
    tag_service: TagService = Depends(get_tag_service),
    sequence: DocumentSequence = Depends(get_sequence),
) -> Tag:
    ret = await tag_service.create_reference(tag_id, sequence, payload.model_dump())
    return Tag(ret)


@tags_router.delete("/{tag_id}/references/{reference_id}")
async def delete_a_reference(
    tag_id: UUID,
    reference_id: str,
    tag_service: TagService = Depends(get_tag_service),
    sequence: DocumentSequence = Depends(get_sequence),
) -> Tag:
    ret = await tag_service.delete_reference(tag_id, sequence, reference_id)
    return Tag(ret)


@tags_router.put("/{tag_id}/references/{reference_id}")
async def update_a_reference_on_the_supplied_tag(
    tag_id: UUID,
    reference_id: str,
    payload: Reference,
    tag_service: TagService = Depends(get_tag_service),
    sequence: DocumentSequence = Depends(get_sequence),
) -> Tag:
    ret = await tag_service.update_reference(tag_id, sequence, reference_id, payload.model_dump())
    return Tag(ret)


@tags_router.post("/{tag_id}/patterns")
async def add_a_new_pattern(tag_id: UUID, new_pattern: Pattern) -> Tag: ...


@tags_router.delete("/{tag_id}/references/{pattern_id}")
async def delete_a_pattern_from_a_tag(tag_id: UUID, pattern_id: str) -> Tag: ...


@tags_router.put("/{tag_id}/references/{pattern_id}")
async def update_the_supplied_pattern_for_a_tag(tag_id: UUID, pattern_id: str) -> Tag: ...
