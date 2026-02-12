"""Tests for main Vigicrues client."""

import pytest
from unittest.mock import patch, Mock
from aioresponses import aioresponses

import aiohttp

from vigicrues import Vigicrues
from vigicrues.models import StationDetails
from tests.conftest import add_response


@pytest.fixture
def mock_get_station_details():
    with patch("vigicrues.client.Vigicrues.get_station_details") as mock:
        mock.return_value = StationDetails(
            id="O408101001",
            name="Le Tarn à Rabastens - Saint-Sulpice",
            has_height_data=True,
            has_flow_data=False,
            river="Tarn",
            city="Rabastens - Saint-Sulpice",
            latitude=43.9000,
            longitude=1.9000,
            picture_url=None,
            commune_code=None,
            is_prediction_station=False,
            has_predictions=False,
            historical_floods=[],
            related_stations=[],
        )
        yield mock


@pytest.mark.asyncio
async def test_search_stations_with_details(
    mock_aioresponses: aioresponses, mock_get_station_details
) -> None:
    """Test main client with context manager."""
    add_response(
        mock_aioresponses,
        "GET",
        r"^https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/referentiel-des-stations-du-reseau-vigicrues/records.*$",
        body={
            "total_count": 1,
            "results": [
                {
                    "cdstationhydro": "O408101001",
                    "lbstationhydro": "Le Tarn à Rabastens - Saint-Sulpice",
                }
            ],
        },
    )

    async with Vigicrues() as client:
        stations = await client.search_stations("Sulpice", check=True)

        assert len(stations) == 1
        assert stations[0].id == "O408101001"
        assert stations[0].name == "Le Tarn à Rabastens - Saint-Sulpice"
        assert stations[0].river == "Tarn"


@pytest.mark.asyncio
async def test_search_stations_filtered(
    mock_aioresponses: aioresponses, mock_get_station_details
) -> None:
    """Test main client with context manager."""
    add_response(
        mock_aioresponses,
        "GET",
        r"^https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/referentiel-des-stations-du-reseau-vigicrues/records.*$",
        body={
            "total_count": 1,
            "results": [
                {
                    "cdstationhydro": "O408101001",
                    "lbstationhydro": "Le Tarn à Rabastens - Saint-Sulpice",
                }
            ],
        },
    )
    mock_get_station_details.side_effect = aiohttp.ClientResponseError(
        request_info=Mock(), history=Mock(), status=404, message="Not Found"
    )

    async with Vigicrues() as client:
        stations = await client.search_stations("Sulpice", check=True)

        assert len(stations) == 0
