from pydantic import BaseModel, Field
from typing import List, Optional


class ImageSizeIn(BaseModel):
    sm: str
    md: str
    lg: str

    model_config = {
        "extra": "forbid",
    }


class SectionIn(BaseModel):
    title: str
    paragraphs: List[str]
    model_config = {
        "extra": "forbid",
    }


class BiographyIn(BaseModel):
    id: str = Field(alias="_id")
    title: str
    image: ImageSizeIn
    sections: List[SectionIn]

    model_config = {
        "extra": "forbid",
        "populate_by_name": True
    }

class BiographyCreateIn(BaseModel):
    title: str
    image: ImageSizeIn
    sections: List[SectionIn]
    user_id: str

    model_config = {
        "extra": "forbid",
        "populate_by_name": True
    }