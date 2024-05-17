from uuid import UUID

from fastapi import APIRouter

comment_router = APIRouter(prefix="/comments", tags=["Comments"])


@comment_router.get("/{comment_id}")
def get_a_single_comment_by_id(comment_id: UUID): ...


@comment_router.delete("/{comment_id}")
def delete_a_comment(comment_id: UUID): ...


@comment_router.put("/{comment_id}")
def update_a_comment(comment_id: UUID): ...


@comment_router.get("/tags/{tag_id}", tags=["Paginated"])
def list_all_comments_for_a_given_tag(tag_id: UUID): ...


@comment_router.post("/tags/{tag_id}")
def create_new_comment_for_a_tag(tag_id: UUID): ...


@comment_router.put("/tags/{tag_id}/private")
def sets_the_private_comment_for_a_tag(tag_id: UUID): ...


@comment_router.delete("/tags/{tag_id}/private")
def deletes_the_private_comment_for_a_tag(tag_id: UUID): ...
