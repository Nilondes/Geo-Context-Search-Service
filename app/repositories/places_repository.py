from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.place import Place


class PlacesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, place_id: int) -> Optional[Place]:
        stmt = select(Place).where(Place.id == place_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, place: Place) -> Place:
        self.session.add(place)
        await self.session.commit()
        await self.session.refresh(place)
        return place

    async def find_nearest(
        self,
        latitude: float,
        longitude: float,
        radius_m: float = 500,
        limit: int = 10,
        category: Optional[str] = None,
        brand: Optional[str] = None,
    ) -> List[Place]:
        """
        Search for nearest places radius_m (meters)
        """

        point = func.ST_SetSRID(
            func.ST_MakePoint(longitude, latitude),
            4326,
        ).cast(Place.geog.type)

        stmt = (
            select(Place)
            .where(
                func.ST_DWithin(
                    Place.geog,
                    point,
                    radius_m,
                )
            )
            .order_by(
                func.ST_Distance(Place.geog, point)
            )
            .limit(limit)
        )

        if category:
            stmt = stmt.where(Place.category == category)

        if brand:
            stmt = stmt.where(Place.brand.ilike(f"%{brand}%"))

        result = await self.session.execute(stmt)
        return result.scalars().all()
