from typing import Annotated, Union, List

from pydantic import Field

from app.lib.constants import TagTypes, TagVisibilityStates

TagName = Annotated[
    str,
    Field(
        title="The name of the tag.",
        examples=["Emotet", "Gooloader", "Cookie Monster"],
        description="The human-readable name for a tag.",
        pattern=r"^[A-Za-z0-9 ._-]+$",
        max_length=255,
    ),
]

TagDescription = Annotated[
    str,
    Field(
        title="The description of the tag.  Used to store additional information about the entity. Make it descriptive "
        "and meaningful!"
    ),
]

TagGroup = Annotated[
    str, Field(title="A group to which the tag belongs (this is an arbitrary string used to group tags into buckets)")
]

TagType = Annotated[
    TagTypes,
    Field(
        title="The type of the tag in question",
    ),
]

TagVisibility = Annotated[
    TagVisibilityStates,
    Field(
        title="Visibility state for the tag",
        description="This value determines various things... idk idk",  # TODO: write.
    ),
]

# Pattern stuff
# TODO: build out proper validation here
TagPatternField = Annotated[str, Field(title="The field to query")]

TagPatternOperator = Annotated[str, Field(title="The operator for the pattern")]  # TODO: Validation required

TagPatternValue = Annotated[
    Union[str, int, List[str], List[int]], Field(title="The 'value' (thing being matched against) for this clause")
]
