import pytest
from unittest.mock import AsyncMock, patch

from app.services.geo_service import GeoService
from app.services.context_parser import ParsedContext
from app.models.schemas import SearchRequest
from app.models.place import Place


@pytest.mark.asyncio
async def test_search_parses_context_and_calls_repository():
    session = AsyncMock()

    service = GeoService(session)

    with patch("app.services.geo_service.parse_context") as mock_parser:
        mock_parser.return_value = ParsedContext(
            category="продукты",
            brand="Магнит",
        )

        fake_place = Place(
            id=1,
            name="Магнит",
            category="продукты",
            brand="Магнит",
            address="Набережная Северной Двины, 30",
            geog="POINT(30 60)",
            source=None,
            metadata_json=None,
        )

        service.find_nearest_places = AsyncMock(
            return_value=[
                {
                    "place": fake_place,
                    "distance_meters": 120.0,
                    "latitude": 60.0,
                    "longitude": 30.0,
                }
            ]
        )

        request = SearchRequest(
            location="64.5430:40.5369",
            context="купить продукты в Магните"
        )

        response = await service.search(request)

        mock_parser.assert_called_once_with("купить продукты в Магните")

        service.find_nearest_places.assert_awaited_once_with(
            latitude=64.5430,
            longitude=40.5369,
            category="продукты",
            brand="Магнит",
            street=None,
        )

        assert len(response.results) == 1
        assert response.results[0].name == "Магнит"
        assert response.results[0].distance_meters == 120.0


@pytest.mark.asyncio
async def test_search_invalid_location_returns_empty():
    session = AsyncMock()
    service = GeoService(session)

    request = SearchRequest.model_construct(
        location="bad:coords",
        context="купить продукты",
    )

    response = await service.search(request)
    assert response.results == []
