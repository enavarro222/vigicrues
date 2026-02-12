"""Tests for VigicruesClient."""
import aiohttp
from aiohttp import ClientSession
import re

import pytest
from aioresponses import aioresponses

from vigicrues.vigicrues import VigicruesClient
from tests.conftest import add_response


@pytest.mark.asyncio
async def test_get_troncons_success(mock_aioresponses: aioresponses, session: ClientSession) -> None:
    """Test successful troncons retrieval."""
    add_response(
        mock_aioresponses,
        "GET",
        r"^https://www.vigicrues.gouv.fr/services/v1.1/TerEntVigiCru.json.*$",
        body={
            "ListEntVigiCru": [
                {
                    "aNMoinsUn": [
                        {
                            "CdEntVigiCruInferieur": "TL12",
                            "LbEntVigiCruInferieur": "Célé"
                        }
                    ]
                }
            ]
        }
    )

    client = VigicruesClient(session=session)
    troncons = await client.get_troncons("25")

    assert len(troncons) == 1
    assert troncons[0].id == "TL12"
    assert troncons[0].name == "Célé"


@pytest.mark.asyncio
async def test_get_troncons_empty_id(mock_aioresponses: aioresponses, session: ClientSession) -> None:
    """Test territories with empty ID."""
    client = VigicruesClient(session=session)
    with pytest.raises(ValueError, match="Territory ID cannot be empty"):
        await client.get_troncons("")


@pytest.mark.asyncio
async def test_get_troncons_no_session(mock_aioresponses: aioresponses) -> None:
    """Test territories with empty ID."""
    client = VigicruesClient(session=None)
    with pytest.raises(RuntimeError):
        await client.get_troncons("25")


@pytest.mark.asyncio
async def test_get_troncons_http_error(mock_aioresponses: aioresponses, session: ClientSession) -> None:
    """Test troncons with HTTP error."""
    add_response(
        mock_aioresponses,
        "GET",
        "https://www.vigicrues.gouv.fr/services/v1.1/TerEntVigiCru.json",
        status=500
    )

    client = VigicruesClient(session=session)
    with pytest.raises(aiohttp.ClientResponseError):
        await client.get_troncons("25")

