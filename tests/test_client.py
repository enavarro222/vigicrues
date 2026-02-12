"""Tests for main Vigicrues client."""

import aiohttp
import pytest
from aioresponses import aioresponses

from vigicrues import Vigicrues
from tests.conftest import add_response


@pytest.mark.asyncio
async def test_main_client_context_manager(mock_aioresponses: aioresponses) -> None:
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

    add_response(
        mock_aioresponses,
        "GET",
        "https://www.vigicrues.gouv.fr/services/TerEntVigiCru.json",
        body={
            "ListEntVigiCru": [
                {"CdEntVigiCru": "25", "LbEntVigiCru": "Garonne-Tarn-Lot"}
            ]
        },
    )

    async with Vigicrues() as client:
        stations = await client.search_stations("Sulpice")
        territories = await client.get_territories()

        assert len(stations) == 1
        assert stations[0].id == "O408101001"
        assert stations[0].name == "Le Tarn à Rabastens - Saint-Sulpice"

        assert len(territories) == 1
        assert territories[0].id == "25"
        assert territories[0].name == "Garonne-Tarn-Lot"


@pytest.mark.asyncio
async def test_main_client_external_session(mock_aioresponses: aioresponses) -> None:
    """Test main client with external session."""
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

    async with aiohttp.ClientSession() as session:
        client = Vigicrues(session=session)
        stations = await client.search_stations("Sulpice")

        assert len(stations) == 1
        assert stations[0].id == "O408101001"
        assert stations[0].name == "Le Tarn à Rabastens - Saint-Sulpice"

        # Verify session is not closed by client
        assert not session.closed


@pytest.mark.asyncio
async def test_main_client_timeout(mock_aioresponses: aioresponses) -> None:
    """Test main client with custom timeout."""
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

    async with Vigicrues(timeout=10.0) as client:
        stations = await client.search_stations("Sulpice")

        assert len(stations) == 1
        assert stations[0].id == "O408101001"
        assert stations[0].name == "Le Tarn à Rabastens - Saint-Sulpice"


@pytest.mark.asyncio
async def test_main_client_http_error(mock_aioresponses: aioresponses) -> None:
    """Test main client with HTTP error."""
    add_response(
        mock_aioresponses,
        "GET",
        r"^https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/referentiel-des-stations-du-reseau-vigicrues/records.*$",
        status=500,
    )

    async with Vigicrues() as client:
        with pytest.raises(aiohttp.ClientResponseError):
            await client.search_stations("Sulpice")
