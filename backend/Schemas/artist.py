from pydantic import BaseModel, Field


class TrackIn(BaseModel):
    trackNumber: int = Field(gt=0)
    title: str = Field(min_length=1)
    src: str = Field(min_length=1)
    tags: list[str] = []

    model_config = {
        "extra": "forbid",
    }


class AlbumIn(BaseModel):
    slug: str
    title: str
    order: int
    tracks: list[TrackIn]

    model_config = {
        "extra": "forbid",
    }


class ArtistIn(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    slug: str
    title: str
    order: int
    albums: list[AlbumIn]

    model_config = {
        "extra": "forbid",
        "populate_by_name": True
    }
