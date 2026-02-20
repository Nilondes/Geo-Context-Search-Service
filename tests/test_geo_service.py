import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import AsyncSessionLocal
from app.models.place import Place
from app.services.geo_service import GeoService


@pytest.mark.asyncio
async def test_find_nearest_places():
    async with AsyncSessionLocal() as session:
        place = Place(
            name="Test Cafe",
            category="cafe",
            brand="TestBrand",
            address="Archangelsk",
            geog="SRID=4326;POINT(37.6176 55.7558)",
            source="test",
        )

        session.add(place)
        await session.commit()

        service = GeoService(session)

        results = await service.find_nearest_places(
            latitude=55.7558,
            longitude=37.6176,
            radius_m=1000,
        )

        assert len(results) >= 1
        assert results[0].name == "Test Cafe"
