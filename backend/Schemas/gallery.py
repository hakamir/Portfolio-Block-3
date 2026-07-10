from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class GalleryImageIn(BaseModel):
    src: str = ''
    title: str = Field(min_length=1)
    location: str = Field(min_length=1)
    date: datetime
    order: int = Field(gt=0)
    alt: Optional[str] = None

    model_config = {
        "extra": "forbid",
    }


class GalleryIn(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    slug: str = ''
    title: str = Field(min_length=1)
    order: int = Field(gt=0)
    images: List[GalleryImageIn]

    model_config = {
        "extra": "forbid",
        "populate_by_name": True
    }
