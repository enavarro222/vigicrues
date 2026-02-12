"""Tests for VigicruesClient."""

import aiohttp
from aiohttp import ClientSession
import re

import pytest
from aioresponses import aioresponses

from vigicrues.vigicrues import VigicruesClient
from tests.conftest import add_response


@pytest.mark.asyncio
async def test_get_troncon_stations_success(
    mock_aioresponses: aioresponses, session: ClientSession
) -> None:
    """Test successful troncon stations retrieval."""
    add_response(
        mock_aioresponses,
        "GET",
        r"^https://www.vigicrues.gouv.fr/services/v1.1/TronEntVigiCru.json.*$",
        body={
            "ListEntVigiCru": [
                {
                    "aNMoinsUn": [
                        {
                            "CdEntVigiCruInferieur": "O811352001",
                            "LbEntVigiCruInferieur": "Figeac",
                        }
                    ]
                }
            ]
        },
    )

    client = VigicruesClient(session=session)
    stations = await client.get_troncon_stations("TL12")

    assert len(stations) == 1
    assert stations[0].id == "O811352001"
    assert stations[0].name == "Figeac"


@pytest.mark.asyncio
async def test_get_troncon_stations_no_session(mock_aioresponses: aioresponses) -> None:
    """Test troncon stations with empty ID."""
    client = VigicruesClient(session=None)
    with pytest.raises(RuntimeError):
        await client.get_troncon_stations("TL12")


@pytest.mark.asyncio
async def test_get_troncon_stations_empty_id(
    mock_aioresponses: aioresponses, session: ClientSession
) -> None:
    """Test troncon stations with empty ID."""
    client = VigicruesClient(session=session)
    with pytest.raises(ValueError, match="Troncon ID cannot be empty"):
        await client.get_troncon_stations("")


@pytest.mark.asyncio
async def test_get_troncon_stations_http_error(
    mock_aioresponses: aioresponses, session: ClientSession
) -> None:
    """Test troncon stations with HTTP error."""
    add_response(
        mock_aioresponses,
        "GET",
        r"^https://www.vigicrues.gouv.fr/services/v1.1/TronEntVigiCru.json.*$",
        status=500,
    )

    client = VigicruesClient(session=session)
    with pytest.raises(aiohttp.ClientResponseError):
        await client.get_troncon_stations("TL12")
