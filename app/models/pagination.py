from typing import Optional, Annotated, List

from pydantic import BaseModel

from app.models.tag import Tag, TagHistory


class FilteringArgs(BaseModel):
    q: Optional[Annotated[str, "The Lucene Query String used to filter returned results"]] = ""


class SortingArgs(BaseModel):
    sort_by: Optional[Annotated[str, "The name of the field to sort by, defaulting to created timestamp"]] = "created"
    sort_order: Optional[Annotated[str, "The direction to sort by, defaulting to ascending"]] = "asc"


class PaginationArgs(BaseModel):
    limit: Optional[Annotated[int, "The maximum number of records to return per page"]] = 10
    offset: Optional[Annotated[int, "The index in the array of results at which to start reading"]] = 0


class PaginationLinkObject(BaseModel):
    first: str
    last: str
    next: Optional[str] = ""
    previous: Optional[str] = ""


class PaginatedModelBase(BaseModel):
    """A model for sending a paginated response to the user."""

    limit: int
    offset: int
    total: int
    # links: PaginationLinkObject


class PaginatedTagList(PaginatedModelBase):
    items: List[Tag] = []


class PaginatedTagHistoryList(PaginatedModelBase):
    items: List[TagHistory] = []


# class PaginatedAuditList(PaginatedModelBase):
#     items: List[] = []
#
#
# class PaginatedCommentList(PaginatedModelBase):
#     items: List[] = []
