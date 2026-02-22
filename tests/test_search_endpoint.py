import pytest
from app.models.place import Place


@pytest.mark.asyncio
async def test_search_returns_results(client, db_session):
    place = Place(
        name="Аптека на Троицком",
        category="аптека",
        brand=None,
        address="Троицкий проспект, 35",
        geog="SRID=4326;POINT(40.5386 64.5426)",
        source="test",
    )

    db_session.add(place)
    await db_session.commit()

    response = await client.post(
        "/search",
        json={
            "location": "64.5430:40.5369",
            "context": "Купить лекарства в аптеке на Троицком",
        },
    )

    if response.status_code != 200:
        print(f"Error: {response.text}")

    assert response.status_code == 200

    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["name"] == "Аптека на Троицком"


@pytest.mark.asyncio
async def test_search_returns_empty_when_no_matches(client):
    response = await client.post(
        "/search",
        json={
            "location": "64.5430:40.5369",
            "context": "найди заправку",
        },
    )

    assert response.status_code == 200
    assert response.json()["results"] == []


@pytest.mark.asyncio
async def test_search_brand_match(client, db_session):
    place = Place(
        name="Чемпион Зоомаркет",
        category="зоомагазин",
        brand="Чемпион",
        address="Воскресенская ул., 7",
        geog="SRID=4326;POINT(40.5359 64.5442)",
        source="test",
    )

    db_session.add(place)
    await db_session.commit()

    response = await client.post(
        "/search",
        json={
            "location": "64.5430:40.5369",
            "context": "Купить корм в Чемпионе",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["name"] == "Чемпион Зоомаркет"


@pytest.mark.asyncio
async def test_search_invalid_location_returns_422(client):
    response = await client.post(
        "/search",
        json={
            "location": "bad:coords",
            "context": "Купить продукты",
        },
    )

    assert response.status_code == 422
