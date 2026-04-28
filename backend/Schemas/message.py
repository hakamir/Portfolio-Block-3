from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class MessageIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    message: str = Field(min_length=1)
    date: Optional[datetime] = None
    read: bool = False
    trashed: bool = False

    model_config = {'extra': 'forbid'}

class MessageUpdate(BaseModel):
    read: Optional[bool] = None
    trashed: Optional[bool] = None

    model_config = {'extra': 'forbid'}