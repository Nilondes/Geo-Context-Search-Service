from typing import Optional, List

from sqlalchemy import select, func, cast
from sqlalchemy.ext.asyncio import AsyncSession

from geoalchemy2 import Geometry

from app.models.place import Place


class PlacesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_nearest(
        self,
        latitude: float,
        longitude: float,
        radius_m: float = 500,
        limit: int = 10,
        category: Optional[str] = None,
        brand: Optional[str] = None,
    ) -> List[dict]:

        point = func.ST_SetSRID(
            func.ST_MakePoint(longitude, latitude),
            4326,
        )

        distance_expr = func.ST_Distance(Place.geog, point)

        stmt = (
            select(
                Place,
                distance_expr.label("distance_meters"),
                func.ST_Y(cast(Place.geog, Geometry("POINT", srid=4326))).label("latitude"),
                func.ST_X(cast(Place.geog, Geometry("POINT", srid=4326))).label("longitude"),
            )
            .where(func.ST_DWithin(Place.geog, point, radius_m))
            .order_by(distance_expr)
            .limit(limit)
        )

        if category:
            stmt = stmt.where(Place.category == category)

        if brand:
            stmt = stmt.where(Place.brand == brand)

        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            {
                "place": row[0],
                "distance_meters": row.distance_meters,
                "latitude": row.latitude,
                "longitude": row.longitude,
            }
            for row in rows
        ]
