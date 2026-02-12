"""DiscoveryClient for searching stations via OpenDataSoft API."""

from __future__ import annotations

import aiohttp
from typing import List, Dict

from .models import Station


class DiscoveryClient:
    """Client for searching stations via OpenDataSoft API."""

    DISCOVERY_BASE_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/referentiel-des-stations-du-reseau-vigicrues"

    def __init__(self, session: aiohttp.ClientSession | None = None) -> None:
        """Initialize DiscoveryClient with optional session and timeout.

        Args:
            session: aiohttp session.
        """
        self._session = session

    def _process_station_result(self, station_data: Dict[str, str]) -> Station | None:
        """Process a single station result from the API response.

        Args:
            result: A single result dictionary from the API response

        Returns:
            Station object if valid and active, None if invalid or closed
        """
        if "cdstationhydro" not in station_data or "lbstationhydro" not in station_data:
            raise ValueError("Invalid station data")

        # Filter out closed stations
        if station_data.get("dtfermeturestationhydro") is not None:
            return None

        return Station(
            id=station_data["cdstationhydro"],
            name=station_data["lbstationhydro"],
        )

    async def search_stations(self, query: str) -> List[Station]:
        """Search for stations by name or location.

        Args:
            query: Search term (station name, city, etc.)

        Returns:
            List of matching stations

        Raises:
            ValueError: If query is empty
            aiohttp.ClientError: For HTTP errors
            json.JSONDecodeError: If response is not valid JSON
            ValidationError: If response data is invalid
        """
        if not query:
            raise ValueError("Query cannot be empty")

        params: Dict[str, str | int] = {
            "where": f'search(lbstationhydro, "{query}")',
            "limit": 20,
            "offset": 0,
        }

        if self._session is None:
            raise RuntimeError("Session is not initialized")
        async with self._session.get(
            f"{self.DISCOVERY_BASE_URL}/records", params=params
        ) as response:
            response.raise_for_status()
            data = await response.json()
            if not isinstance(data, dict):
                raise ValueError("Got invalid data")
            results = data.get("results", [])
            return [
                station
                for result in results
                if (station := self._process_station_result(result)) is not None
            ]
