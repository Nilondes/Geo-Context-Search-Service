import pytest
from unittest.mock import AsyncMock, patch

from app.services.geo_service import GeoService
from app.models.schemas import SearchRequest
from app.models.place import Place


@pytest.mark.asyncio
async def test_search_parses_context_and_calls_repository():
    session = AsyncMock()

    service = GeoService(session)

    with patch("app.services.geo_service.parse_context") as mock_parser:
        mock_parser.return_value = {
            "category": "coffee",
            "brand": "starbucks",
        }

        fake_place = Place(
            id=1,
            name="Starbucks Central",
            category="coffee",
            brand="starbucks",
            address="Test street",
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
            location="60.0:30.0",
            context="где ближайший старбакс"
        )

        response = await service.search(request)

        mock_parser.assert_called_once_with("где ближайший старбакс")

        service.find_nearest_places.assert_awaited_once_with(
            latitude=60.0,
            longitude=30.0,
            category="coffee",
            brand="starbucks",
        )

        assert len(response.results) == 1
        assert response.results[0].name == "Starbucks Central"
        assert response.results[0].distance_meters == 120.0
