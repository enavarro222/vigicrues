"""Test configuration for Vigicrues client."""
import json
import pytest
import re
from aioresponses import aioresponses
from aiohttp import ClientSession, ClientTimeout
from typing import Any

from vigicrues import Vigicrues


@pytest.fixture
def mock_aioresponses() -> aioresponses:
    """Fixture for aioresponses mock."""
    with aioresponses() as mock:
        yield mock

@pytest.fixture
async def session() -> ClientSession:
    async with ClientSession(timeout=ClientTimeout(total=3)) as session:
        yield session

@pytest.fixture
async def vigicrues_client(mock_aioresponses: aioresponses) -> Vigicrues:
    """Fixture for Vigicrues client with mocked responses."""
    client = Vigicrues()
    await client.__aenter__()
    yield client
    await client.__aexit__(None, None, None)


def add_response(
    mock: aioresponses,
    method: str,
    url: str,
    status: int = 200,
    body: Any = None,
    repeat: int = 1,
    **kwargs
) -> None:
    """Helper function to mock HTTP responses."""
    if body is None:
        body = {}

    pattern = re.compile(url)
    mock.add(
        method=method,
        url=pattern,
        status=status,
        body=json.dumps(body),
        repeat=repeat,
        content_type="application/json",
        **kwargs
    )
