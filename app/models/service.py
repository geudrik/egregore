from dataclasses import dataclass
from typing import List


@dataclass
class ReturnModel:
    """A class that all CRUD service methods should be returning. This ensures that Audit entries all have unique
    messages

    :arg data: The data to return, either a dict, or list of dicts that represent complete ES docs
    :arg audit_message: Optional. The message consumed by the @audit decorator when it's used
    :arg total: Optional. The total number of items in the index, only used for listing methods
    :arg limit: Optional. The limit used in the query, only used for listing methods
    :arg offset: Optional. The offset used in the query, only used for listing methods
    """

    data: dict | List[dict] = None
    audit_message: str = None

    # Specific to paginated (listing) methods
    total: int = 0
    limit: int = 0
    offset: int = 0
