"""Tests for DiscoveryClient."""

import aiohttp
from aiohttp import ClientSession
import pytest
from aioresponses import aioresponses

from pydantic import ValidationError

from vigicrues.discovery import DiscoveryClient
from tests.conftest import add_response


@pytest.mark.asyncio
async def test_search_stations_success(
    mock_aioresponses: aioresponses, session: ClientSession
) -> None:
    """Test successful station search."""
    add_response(
        mock_aioresponses,
        "GET",
        "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/referentiel-des-stations-du-reseau-vigicrues/records",
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

    client = DiscoveryClient(session)
    stations = await client.search_stations("Sulpice")

    assert len(stations) == 1
    assert stations[0].id == "O408101001"
    assert stations[0].name == "Le Tarn à Rabastens - Saint-Sulpice"


@pytest.mark.asyncio
async def test_search_stations_empty_query(
    mock_aioresponses: aioresponses, session: ClientSession
) -> None:
    """Test search with empty query."""
    client = DiscoveryClient(session)
    with pytest.raises(ValueError, match="Query cannot be empty"):
        await client.search_stations("")


@pytest.mark.asyncio
async def test_search_stations_http_error(
    mock_aioresponses: aioresponses, session: ClientSession
) -> None:
    """Test search with HTTP error."""
    add_response(
        mock_aioresponses,
        "GET",
        "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/referentiel-des-stations-du-reseau-vigicrues/records",
        status=500,
    )

    client = DiscoveryClient(session)
    with pytest.raises(aiohttp.ClientResponseError):
        await client.search_stations("Sulpice")


@pytest.mark.asyncio
async def test_search_stations_no_session(mock_aioresponses: aioresponses) -> None:
    """Test search when no session given."""
    client = DiscoveryClient(None)
    with pytest.raises(RuntimeError):
        await client.search_stations("Sulpice")


@pytest.mark.asyncio
async def test_search_stations_invalid_json(
    mock_aioresponses: aioresponses, session: ClientSession
) -> None:
    """Test search with invalid JSON response."""
    add_response(
        mock_aioresponses,
        "GET",
        r"^https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/referentiel-des-stations-du-reseau-vigicrues/records.*$",
        status=200,
        body="invalid json",
        headers={"content_type": "application/json"},
    )

    client = DiscoveryClient(session)
    with pytest.raises(ValueError):
        await client.search_stations("Sulpice")


@pytest.mark.asyncio
async def test_search_stations_invalid_data(
    mock_aioresponses: aioresponses, session: ClientSession
) -> None:
    """Test search with invalid data."""
    add_response(
        mock_aioresponses,
        "GET",
        r"^https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/referentiel-des-stations-du-reseau-vigicrues/records.*$",
        body={"total_count": 1, "results": [{"fields": {"invalid_field": "value"}}]},
    )

    client = DiscoveryClient(session)
    with pytest.raises(ValidationError):
        stations = await client.search_stations("Sulpice")
