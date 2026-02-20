from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.place import Place
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
            limit: int = 10,
            category: Optional[str] = None,
            brand: Optional[str] = None,
    ) -> List[Place]:

        rows = await self.repository.find_nearest(
            latitude=latitude,
            longitude=longitude,
            radius_m=radius_m,
            limit=limit,
            category=category,
            brand=brand,
        )

        return [row["place"] for row in rows]

    async def search(self, request: SearchRequest) -> SearchResponse:

        parsed = parse_context(request.context)

        def _get(obj, key):
            if obj is None:
                return None
            if isinstance(obj, dict):
                return obj.get(key)
            return getattr(obj, key, None)

        category = _get(parsed, "category")
        brand = _get(parsed, "brand")

        try:
            lat_str, lon_str = request.location.split(":")
            latitude = float(lat_str.strip())
            longitude = float(lon_str.strip())
        except Exception:
            return SearchResponse(results=[])


        places = await self.find_nearest_places(
            latitude=latitude,
            longitude=longitude,
            category=category,
            brand=brand,
        )

        results = [
            SearchResult(
                name=item["place"].name,
                latitude=item["latitude"],
                longitude=item["longitude"],
                distance_meters=item["distance_meters"],
            )
            for item in places
        ]

        return SearchResponse(results=results)
