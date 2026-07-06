from typing import Optional

from pydantic import BaseModel, Field


class CreateUser(BaseModel):
    lastname: Optional[str] = ""
    firstname: Optional[str] = ""
    email: str
    password: str = Field(min_length=12)
    role: str = Field(default='artist')
    model_config = {'extra': 'forbid'}