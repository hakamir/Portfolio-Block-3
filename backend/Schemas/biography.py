from pydantic import BaseModel, Field
from typing import List, Optional

class SectionIn(BaseModel):
    title: str
    paragraphs: List[str]
    model_config = {
        "extra": "forbid",
    }


class BiographyIn(BaseModel):
    title: str
    sections: List[SectionIn]

    model_config = {
        "extra": "forbid",
        "populate_by_name": True
    }

class BiographyCreateIn(BaseModel):
    title: str
    sections: List[SectionIn]
    user_id: str
    model_config = {
        "extra": "forbid",
        "populate_by_name": True
    }