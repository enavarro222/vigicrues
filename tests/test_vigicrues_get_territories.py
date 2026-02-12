"""Tests for VigicruesClient."""
import aiohttp
from aiohttp import ClientSession
import re

import pytest
from aioresponses import aioresponses

from vigicrues.vigicrues import VigicruesClient
from tests.conftest import add_response


@pytest.mark.asyncio
async def test_get_territories_success(mock_aioresponses: aioresponses, session: ClientSession) -> None:
    """Test successful territories retrieval."""
    add_response(
        mock_aioresponses,
        "GET",
        "https://www.vigicrues.gouv.fr/services/TerEntVigiCru.json",
        body={
            "ListEntVigiCru": [
                {
                    "CdEntVigiCru": "25",
                    "LbEntVigiCru": "Garonne-Tarn-Lot"
                }
            ]
        }
    )

    client = VigicruesClient(session=session)
    territories = await client.get_territories()

    assert len(territories) == 1
    assert territories[0].id == "25"
    assert territories[0].name == "Garonne-Tarn-Lot"


@pytest.mark.asyncio
async def test_get_territories_no_session(mock_aioresponses: aioresponses) -> None:
    """Test territories when no session given."""
    client = VigicruesClient(session=None)
    with pytest.raises(RuntimeError):
        await client.get_territories()


@pytest.mark.asyncio
async def test_get_territories_http_error(mock_aioresponses: aioresponses, session: ClientSession) -> None:
    """Test territories with HTTP error."""
    add_response(
        mock_aioresponses,
        "GET",
        "https://www.vigicrues.gouv.fr/services/TerEntVigiCru.json",
        status=500
    )

    client = VigicruesClient(session=session)
    with pytest.raises(aiohttp.ClientResponseError):
        await client.get_territories()

