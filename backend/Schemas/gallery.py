from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class GalleryImageIn(BaseModel):
    src: str
    title: str
    location: Optional[str] = None
    date: Optional[datetime] = None
    order: Optional[int] = None
    alt: Optional[str] = None

    model_config = {
        "extra": "forbid",
    }


class GalleryIn(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    slug: str
    title: str
    order: int
    images: List[GalleryImageIn]

    model_config = {
        "extra": "forbid",
        "populate_by_name": True
    }
