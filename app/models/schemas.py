from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class SearchRequest(BaseModel):
    location: str = Field(
        ...,
        description="Coordinates in format 'latitude:longitude'",
        example="64.5430:40.5369"
    )
    context: str = Field(
        ...,
        description="Natural language search context",
        example="Купить лекарства в аптеке на Троицком"
    )

    @field_validator("location")
    @classmethod
    def validate_location(cls, value):
        try:
            lat, lon = value.split(":")
            float(lat)
            float(lon)
        except Exception:
            raise ValueError("Location must be 'lat:lon'")
        return value

    def parse_location(self) -> tuple[float, float]:
        lat, lon = self.location.split(":")
        return float(lat.strip()), float(lon.strip())


class SearchResult(BaseModel):
    name: str
    latitude: float
    longitude: float
    distance_meters: Optional[float] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
