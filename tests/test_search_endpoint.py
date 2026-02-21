import pytest
from app.models.place import Place


@pytest.mark.asyncio
async def test_search_returns_results(client, db_session):
    place = Place(
        name="Test Cafe",
        category="cafe",
        brand="TestBrand",
        address="Moscow",
        geog="SRID=4326;POINT(37.6176 55.7558)",
        source="test",
    )

    db_session.add(place)
    await db_session.commit()

    response = await client.post(
        "/search",
        json={
            "location": "55.7558:37.6176",
            "context": "найди кафе",
        },
    )

    if response.status_code != 200:
        print(f"Error: {response.text}")

    assert response.status_code == 200

    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["name"] == "Test Cafe"


@pytest.mark.asyncio
async def test_search_returns_empty_when_no_matches(client):
    response = await client.post(
        "/search",
        json={
            "location": "55.7558:37.6176",
            "context": "найди заправку",
        },
    )

    assert response.status_code == 200
    assert response.json()["results"] == []
