from uuid import UUID

from fastapi import APIRouter, Depends
from starlette.responses import RedirectResponse

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
    pagination=Depends(PaginationArgs),
    filtering=Depends(FilteringArgs),
    sorting=Depends(SortingArgs),
) -> PaginatedTagList:
    count, limit, offset, res = await tag_service.list(pagination, filtering, sorting)
    # Convert list of docs into Tag instances for return in our PaginatedTagList model
    ret = [
        Tag(
            **i["_source"],
            id=i["_id"],
            sequence=DocumentSequence(seq_no=i["_seq_no"], primary_term=i["_primary_term"]),
            version=i["_version"],
        )
        for i in res
    ]

    return PaginatedTagList(limit=limit, offset=offset, total=count, items=ret)


@tags_router.get("/{tag_id}")
def get_a_tag_by_id(tag_id: UUID): ...


@tags_router.post("/")
async def create_a_new_tag(
    new_tag: Create,
    tag_service: TagService = Depends(get_tag_service),
):
    ret = await tag_service.create(new_tag.model_dump(), username="demouser")
    return Tag(**ret["_source"], sequence=DocumentSequence(seq_no=ret["_seq_no"], primary_term=ret["_primary_term"]))


@tags_router.patch("/{tag_id}")
def update_an_existing_tag(tag_id: UUID, update_data: Update): ...


@tags_router.delete("/{tag_id}")
def delete_a_tag(tag_id: UUID): ...


@tags_router.get("/{tag_id}/comments", tags=["Comments", "Paginated"])
def list_all_comments_for_a_tag(tag_id: UUID):
    return RedirectResponse(url=f"/comments/tags/{tag_id}", status_code=301)


@tags_router.post("/{tag_id}/comments")
def add_a_comment_to_a_tag(tag_id: UUID):
    return RedirectResponse(url=f"/comments/tags/{tag_id}", status_code=301)


@tags_router.delete("/{tag_id}/comments/{comment_id}")
def delete_a_comment_from_a_tag(tag_id: UUID, comment_id: UUID):
    return RedirectResponse(url=f"/comments/{comment_id}", status_code=301)


@tags_router.put("/{tag_id}/comments/{comment_id}")
def update_a_comment_for_the_supplied_tag(tag_id: UUID, comment_id: UUID) -> RedirectResponse:
    return RedirectResponse(url=f"/comments/{comment_id}", status_code=301)


@tags_router.post("/{tag_id}/references")
def add_a_new_reference(tag_id: UUID, new_reference: Reference): ...


@tags_router.delete("/{tag_id}/references/{reference_id}")
def delete_a_reference(tag_id: UUID, reference_id: str): ...


@tags_router.put("/{tag_id}/references/{reference_id}")
def update_a_reference_on_the_supplied_tag(tag_id: UUID, reference_id: str): ...


@tags_router.post("/{tag_id}/patterns")
def add_a_new_pattern(tag_id: UUID, new_pattern: Pattern): ...


@tags_router.delete("/{tag_id}/references/{pattern_id}")
def delete_a_pattern_from_a_tag(tag_id: UUID, pattern_id: str): ...


@tags_router.put("/{tag_id}/references/{pattern_id}")
def update_the_supplied_pattern_for_a_tag(tag_id: UUID, pattern_id: str): ...
