from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional
from datetime import datetime
import re


class GalleryImageIn(BaseModel):
    src: str
    title: str = Field(min_length=1)
    location: str = Field(min_length=1)
    date: datetime
    order: int = Field(gt=0)
    alt: Optional[str] = None

    model_config = {
        "extra": "forbid",
    }

    @field_validator("src")
    @classmethod
    def validate_image_src(cls, v):
        """ Validate image source format """
        stem, ext = v.rsplit('.', 1)  # Separate extension from stem Ex: stem: slug_uuid, ext: jpg
        slug, uuid_str = stem.rsplit('_', 1)  # Separate slug from uuid Ex: slug: slug, uuid_str: uuid
        is_uuid = re.match(
            r'^[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$', uuid_str
        )
        if not slug:
            raise ValueError("Invalid slug format in image source")
        if not is_uuid:
            raise ValueError("Invalid UUID format in image source")
        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            raise ValueError("Invalid image extension")
        return v


class GalleryIn(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    slug: str = Field(min_length=1)
    title: str = Field(min_length=1)
    order: int = Field(gt=0)
    images: List[GalleryImageIn]

    model_config = {
        "extra": "forbid",
        "populate_by_name": True
    }

    @model_validator(mode="after")
    def validate_image_slug_match(self):
        for img in self.images:
            stem, _ = img.src.rsplit('.', 1)
            slug_from_src, _ = stem.rsplit('_', 1)
            if slug_from_src != self.slug:
                raise ValueError("Image slug does not match gallery slug")
        return self