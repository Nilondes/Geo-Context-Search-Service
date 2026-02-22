import pytest

from app.models.place import Place
from app.services.geo_service import GeoService


@pytest.mark.asyncio
async def test_find_nearest_places_archangelsk_radius_filter(db_session):
    near_place = Place(
        name="Аптека на Троицком",
        category="аптека",
        brand=None,
        address="Троицкий проспект, 35",
        geog="SRID=4326;POINT(40.5386 64.5426)",
        source="test",
    )
    far_place = Place(
        name="Аптека Далеко",
        category="аптека",
        brand=None,
        address="Отдаленный район",
        geog="SRID=4326;POINT(40.5600 64.5500)",
        source="test",
    )

    db_session.add_all([near_place, far_place])
    await db_session.commit()

    service = GeoService(db_session)

    results = await service.find_nearest_places(
        latitude=64.5430,
        longitude=40.5369,
        radius_m=500,
    )

    names = [r["place"].name for r in results]
    assert "Аптека на Троицком" in names
    assert "Аптека Далеко" not in names


@pytest.mark.asyncio
async def test_find_nearest_places_brand_and_category_filter(db_session):
    magnet = Place(
        name="Магнит",
        category="продукты",
        brand="Магнит",
        address="Набережная Северной Двины, 30",
        geog="SRID=4326;POINT(40.5379 64.5419)",
        source="test",
    )
    pyaterochka = Place(
        name="Пятёрочка",
        category="продукты",
        brand="Пятёрочка",
        address="Воскресенская ул., 16",
        geog="SRID=4326;POINT(40.5384 64.5439)",
        source="test",
    )

    db_session.add_all([magnet, pyaterochka])
    await db_session.commit()

    service = GeoService(db_session)

    results = await service.find_nearest_places(
        latitude=64.5430,
        longitude=40.5369,
        radius_m=500,
        category="продукты",
        brand="Магнит",
    )

    assert len(results) >= 1
    assert all(r["place"].brand == "Магнит" for r in results)


@pytest.mark.asyncio
async def test_find_nearest_places_street_filter(db_session):
    troitsky = Place(
        name="Аптека на Троицком",
        category="аптека",
        brand=None,
        address="Троицкий проспект, 35",
        geog="SRID=4326;POINT(40.5386 64.5426)",
        source="test",
    )
    voskresenskaya = Place(
        name="Аптека на Воскресенской",
        category="аптека",
        brand=None,
        address="Воскресенская ул., 3",
        geog="SRID=4326;POINT(40.5352 64.5440)",
        source="test",
    )

    db_session.add_all([troitsky, voskresenskaya])
    await db_session.commit()

    service = GeoService(db_session)

    results = await service.find_nearest_places(
        latitude=64.5430,
        longitude=40.5369,
        radius_m=500,
        category="аптека",
        street="Троицк",
    )

    names = [r["place"].name for r in results]
    assert "Аптека на Троицком" in names
    assert "Аптека на Воскресенской" not in names
