from typing import List, Optional

from pydantic import BaseModel


class User(BaseModel):
    """Model that represents a user object. This would in a real system get populated by some other means and attached
    to the request state. It can then be used to provide RBAC access to routes, as well as pass in to services
    to augment log, audit, etc entries
    """

    username: str
    roles: Optional[List[str]] = []
