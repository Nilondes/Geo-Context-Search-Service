from pydantic import BaseModel, Field
from typing import List, Optional


class SearchRequest(BaseModel):
    location: str = Field(
        ...,
        description="Coordinates in format 'latitude:longitude'",
        example="64.5401:40.5433"
    )
    context: str = Field(
        ...,
        description="Natural language search context",
        example="Купить лекарства в аптеке на Троицком"
    )


class SearchResult(BaseModel):
    name: str
    latitude: float
    longitude: float
    distance_meters: Optional[float] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
