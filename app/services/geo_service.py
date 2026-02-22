from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import SearchRequest, SearchResponse, SearchResult
from app.repositories.places_repository import PlacesRepository
from app.services.context_parser import parse_context


class GeoService:
    def __init__(self, session: AsyncSession):
        self.repository = PlacesRepository(session)

    async def find_nearest_places(
            self,
            latitude: float,
            longitude: float,
            radius_m: float = 500,
            limit: int = 5,
            category: Optional[str] = None,
            brand: Optional[str] = None,
            street: Optional[str] = None,
    ) -> List[dict]:

        rows = await self.repository.find_nearest(
            latitude=latitude,
            longitude=longitude,
            radius_m=radius_m,
            limit=limit,
            category=category,
            brand=brand,
            street=street,
        )

        return rows

    async def search(self, request: SearchRequest) -> SearchResponse:

        parsed = parse_context(request.context)

        try:
            latitude, longitude = request.parse_location()
        except Exception:
            return SearchResponse(results=[])

        category = parsed.category
        brand = parsed.brand
        street = parsed.street


        places = await self.find_nearest_places(
            latitude=latitude,
            longitude=longitude,
            category=category,
            brand=brand,
            street=street,
        )

        results = [
            SearchResult(
                name=place_dict["place"].name,
                latitude=place_dict["latitude"],
                longitude=place_dict["longitude"],
                distance_meters=place_dict["distance_meters"],
            )
            for place_dict in places
        ]

        return SearchResponse(results=results)
