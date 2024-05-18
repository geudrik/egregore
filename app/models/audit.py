from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Audit(BaseModel):
    created: datetime
    action: str
    component: str
    subcomponent: Optional[str]
    tag_id: Optional[UUID]
    version: Optional[int]
    message: str
    user: str
