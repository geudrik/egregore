import hashlib
import json
from datetime import datetime
from typing import List, Optional, Annotated
from uuid import UUID

from pydantic import BaseModel, computed_field, Field

from app.lib.constants import TagTypes
from app.models.fields import (
    TagVisibility,
    TagGroup,
    TagDescription,
    TagName,
    TagPatternField,
    TagPatternOperator,
    TagPatternValue,
)
from app.models.sequence import DocumentSequence
from app.models.service import ReturnModel

PatternStart = Annotated[
    Optional[datetime],
    Field(
        title="Start Bound",
        description="An ISO formatted timestamp that acts as the lower bound for the search scope",
        examples=["2024-05-30T22:06:56.292006"],
    ),
]

PatternEnd = Annotated[
    Optional[datetime],
    Field(
        title="End Bound",
        description="An ISO formatted timestamp that acts as the upper bound for the search scope",
        examples=["2024-05-30T22:06:56.292006"],
    ),
]


class Reference(BaseModel):
    """Model representing one reference. Tags can have N references"""

    name: str
    link: str
    description: str
    source: str

    @computed_field(return_type=str)
    @property
    def id(self):
        """The deterministic ID is computed as the sha1 of the URL. This is the only input for generation as everything
        else is human editable"""
        return hashlib.sha1(self.link.encode()).hexdigest()


class PatternClause(BaseModel):
    """Model representing any one Clause for a given Tag pattern (patterns are comprised of N clauses)"""

    field: TagPatternField
    operator: TagPatternOperator
    value: TagPatternValue

    @computed_field(return_type=str)
    @property
    def id(self):
        """The deterministic ID is the sha1 of the field, operator, and value"""
        return hashlib.sha1(f"{self.field}{self.operator}{self.value}".encode()).hexdigest()


class Pattern(BaseModel):
    """Model representing any one pattern of a Tag, Tags have N patterns"""

    start: PatternStart = None
    stop: PatternEnd = None
    operator: str
    clauses: List[PatternClause]

    @computed_field(return_type=str)
    @property
    def id(self):
        # Sort the clauses in this pattern in a deterministic way before hashing it. This ensures that the
        # order of the clauses in the pattern doesn't matter as far as the deterministic ID is concerned
        sorted_data = sorted(self.clauses, key=lambda i: (i.field, i.operator, i.value))
        full = f"{self.operator}{''.join([json.dumps(i.model_dump()) for i in sorted_data])}"
        return hashlib.sha1(full.encode()).hexdigest()


class Create(BaseModel):
    """Model used to describe the creation of a tag."""

    name: TagName
    description: TagDescription
    groups: Optional[List[TagGroup]] = []
    type: TagTypes
    visibility: TagVisibility


class Update(Create):
    """Same as the Create model, but all fields are optional"""

    name: Optional[TagName] = ""
    description: Optional[TagDescription] = ""
    groups: Optional[List[TagGroup]] = []
    type: Optional[TagTypes] = ""
    visibility: Optional[TagVisibility] = ""


class TagBase(Create):
    id: UUID
    created: datetime
    author: str
    updated: datetime
    editor: str
    deleted: Optional[datetime] = None
    related: Optional[List[str]] = []
    state: Optional[str] = ""
    references: Optional[List[Reference]] = []
    patterns: Optional[List[Pattern]] = []
    version: int


class Tag(TagBase):

    def __init__(self, doc: ReturnModel | dict):
        if isinstance(doc, ReturnModel):
            doc = doc.data

        sequence = DocumentSequence(seq_no=doc["_seq_no"], primary_term=doc["_primary_term"])
        super().__init__(
            **doc["_source"],
            sequence=sequence,
            id=doc["_id"],
            version=doc["_version"],
        )

    sequence: DocumentSequence


class TagHistory(TagBase):
    pass
