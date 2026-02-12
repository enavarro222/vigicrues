"""Tests for VigicruesClient."""
import aiohttp
from aiohttp import ClientSession

import pytest
from aioresponses import aioresponses
from pydantic import ValidationError

from vigicrues.vigicrues import VigicruesClient
from tests.conftest import add_response


@pytest.mark.asyncio
async def test_get_station_details_success(mock_aioresponses: aioresponses, session: ClientSession) -> None:
    """Test successful station details retrieval."""
    add_response(
        mock_aioresponses,
        "GET",
        "https://www.vigicrues.gouv.fr/services/station.json/index.php",
        body={
            "LbStationHydro": "Montauban",
            "LbCoursEau": "Tarn",
            "CdCommune": "82121",
            "CoordStationHydro": {
                "CoordXStationHydro": "567613",
                "CoordYStationHydro": "6325598"
            },
            "VigilanceCrues": {
                "Photo": "t",
                "StationPrevision": True,
                "CruesHistoriques": [
                    {
                        "LbUsuel": "Crue du 03/03/1930",
                        "ValHauteur": 11.5,
                        "ValDebit": 0
                    }
                ],
                "StationsBassin": [
                    {
                        "CdStationHydro": "O598101001",
                        "LbStationHydro": "Moissac",
                        "LbCoursEau": "Tarn"
                    }
                ]
            }
        }
    )

    client = VigicruesClient(session=session)
    details = await client.get_station_details("O494101001")

    assert details.name == "Montauban"
    assert details.river == "Tarn"
    assert details.city == "82121"
    assert details.latitude == 567613
    assert details.longitude == 6325598
    assert details.picture_url == "t"
    assert details.is_prediction_station is True
    assert len(details.historical_floods) == 1
    assert len(details.related_stations) == 1


@pytest.mark.asyncio
async def test_get_station_invalid_details(mock_aioresponses: aioresponses, session: ClientSession) -> None:
    """Test successful station details retrieval."""
    add_response(
        mock_aioresponses,
        "GET",
        "https://www.vigicrues.gouv.fr/services/station.json/index.php",
        body={
            "LbStationHydro": "Montauban",
            "LbCoursEau": "Tarn",
            "CdCommune": "82121",
            "CoordStationHydro": {
                "CoordXStationHydro": "aer567613",      # invalid data
                "CoordYStationHydro": "6325598"
            },
            "VigilanceCrues": {
                "Photo": "t",
                "StationPrevision": True,
                "CruesHistoriques": [
                    {
                        "LbUsuel": "Crue du 03/03/1930",
                        "ValHauteur": 11.5,
                        "ValDebit": 0
                    }
                ],
                "StationsBassin": [
                    {
                        "CdStationHydro": "O598101001",
                        "LbStationHydro": "Moissac",
                        "LbCoursEau": "Tarn"
                    }
                ]
            }
        }
    )

    client = VigicruesClient(session=session)
    with pytest.raises(ValidationError):
        await client.get_station_details("O494101001")


@pytest.mark.asyncio
async def test_get_station_details_empty_id(mock_aioresponses: aioresponses, session: ClientSession) -> None:
    """Test station details with empty ID."""
    client = VigicruesClient(session=session)
    with pytest.raises(ValueError, match="Station ID cannot be empty"):
        await client.get_station_details("")

@pytest.mark.asyncio
async def test_get_station_details_no_session(mock_aioresponses: aioresponses) -> None:
    """Test station details with empty ID."""
    client = VigicruesClient(session=None)
    with pytest.raises(RuntimeError):
        await client.get_station_details("O494101001")


@pytest.mark.asyncio
async def test_get_station_details_http_error(mock_aioresponses: aioresponses, session: ClientSession) -> None:
    """Test station details with HTTP error."""
    add_response(
        mock_aioresponses,
        "GET",
        "https://www.vigicrues.gouv.fr/services/station.json/index.php",
        status=500
    )

    client = VigicruesClient(session=session)
    with pytest.raises(aiohttp.ClientResponseError):
        await client.get_station_details("O494101001")
