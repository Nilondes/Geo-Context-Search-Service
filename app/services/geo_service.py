from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.place import Place
from app.repositories.places_repository import PlacesRepository


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
        return await self.repository.find_nearest(
            latitude=latitude,
            longitude=longitude,
            radius_m=radius_m,
            limit=limit,
            category=category,
            brand=brand,
        )
