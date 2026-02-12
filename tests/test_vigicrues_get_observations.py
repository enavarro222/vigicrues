"""Tests for VigicruesClient."""

import aiohttp
from aiohttp import ClientSession
import re

import pytest
from aioresponses import aioresponses

from vigicrues.vigicrues import VigicruesClient
from tests.conftest import add_response


@pytest.mark.asyncio
async def test_get_latest_observations_success(
    mock_aioresponses: aioresponses, session: ClientSession
) -> None:
    """Test successful observations retrieval."""
    add_response(
        mock_aioresponses,
        "GET",
        r"^https://www.vigicrues.gouv.fr/services/observations.json/index.php.*$",
        body={
            "Serie": {
                "ObssHydro": [
                    {"DtObsHydro": "2026-02-12T11:15:00+00:00", "ResObsHydro": 5.41}
                ]
            }
        },
    )

    client = VigicruesClient(session=session)
    observation = await client.get_latest_observations("O408101001", "H")

    assert observation.value == 5.41
    assert observation.type == "H"
    assert observation.unit == "m"
    assert str(observation.timestamp) == "2026-02-12 11:15:00+00:00"


@pytest.mark.asyncio
async def test_get_latest_observations_empty_id(
    mock_aioresponses: aioresponses, session: ClientSession
) -> None:
    """Test observations with empty ID."""
    client = VigicruesClient(session=session)
    with pytest.raises(ValueError, match="Station ID cannot be empty"):
        await client.get_latest_observations("", "H")


@pytest.mark.asyncio
async def test_get_latest_observations_no_session(
    mock_aioresponses: aioresponses,
) -> None:
    """Test observations with empty ID."""
    client = VigicruesClient(session=None)
    with pytest.raises(RuntimeError):
        await client.get_latest_observations("O408101001", "H")


@pytest.mark.asyncio
async def test_get_latest_observations_invalid_type(
    mock_aioresponses: aioresponses, session: ClientSession
) -> None:
    """Test observations with invalid type."""
    client = VigicruesClient(session=session)
    with pytest.raises(
        ValueError, match=re.escape("obs_type must be 'H' (height) or 'Q' (flow)")
    ):
        await client.get_latest_observations("O408101001", "X")


@pytest.mark.asyncio
async def test_get_latest_observations_http_error(
    mock_aioresponses: aioresponses, session: ClientSession
) -> None:
    """Test observations with HTTP error."""
    add_response(
        mock_aioresponses,
        "GET",
        r"^https://www.vigicrues.gouv.fr/services/observations.json/index.php.*$",
        status=500,
    )

    client = VigicruesClient(session=session)
    with pytest.raises(aiohttp.ClientResponseError):
        await client.get_latest_observations("O408101001", "H")


@pytest.mark.asyncio
async def test_get_latest_observations_no_data(
    mock_aioresponses: aioresponses, session: ClientSession
) -> None:
    """Test observations with no data."""
    add_response(
        mock_aioresponses,
        "GET",
        r"^https://www.vigicrues.gouv.fr/services/observations.json/index.php.*$",
        body={"Serie": {"ObssHydro": []}},
    )

    client = VigicruesClient(session=session)
    with pytest.raises(ValueError, match="No observations found"):
        await client.get_latest_observations("O408101001", "H")
