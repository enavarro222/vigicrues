"""Main Vigicrues client combining DiscoveryClient and VigicruesClient."""

from __future__ import annotations

from typing import Optional, Type, List, overload, Literal
from types import TracebackType
import aiohttp

from .discovery import DiscoveryClient
from .vigicrues import VigicruesClient
from .models import Station, StationDetails


class Vigicrues(VigicruesClient, DiscoveryClient):
    """Combined client for Vigicrues and station discovery."""

    def __init__(
        self, session: aiohttp.ClientSession | None = None, timeout: float | None = None
    ) -> None:
        """Initialize client with optional external session and timeout.

        Args:
            session: Optional aiohttp session. If None, an internal session will be created.
            timeout: Optional timeout in seconds for HTTP requests. Default is 30 seconds.
        """
        # Initialize parent classes - they should accept and use self._session
        super().__init__()
        self._session = session
        self._owns_session = session is None
        self._timeout = timeout or 30.0

    async def __aenter__(self) -> "Vigicrues":
        """Enter async context, creating session if needed."""
        if self._owns_session:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self._timeout)
            )
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit async context, closing session only if we own it."""
        if self._owns_session and self._session:
            await self._session.close()

    @overload
    async def search_stations(
        self, query: str, check: Literal[False] = ...
    ) -> list[Station]: ...

    @overload
    async def search_stations(
        self, query: str, check: Literal[True]
    ) -> list[StationDetails]: ...

    async def search_stations(
        self, query: str, check: bool = True
    ) -> List[Station] | List[StationDetails]:
        """Search for stations by name or location with optional validation.

        Args:
            query: Search term (station name, city, etc.)
            check: If True, validate each station by loading its details.
                   If False, return stations without validation.

        Returns:
            List of matching stations

        Raises:
            ValueError: If query is empty
            aiohttp.ClientError: For HTTP errors
            json.JSONDecodeError: If response is not valid JSON
            ValidationError: If response data is invalid
        """
        # Get initial results from parent class
        stations = await super().search_stations(query)

        if not check:
            return stations

        # Validate each station by loading its details
        valid_full_stations = []
        for station in stations:
            try:
                full_station = await self.get_station_details(station.id)
                valid_full_stations.append(full_station)
            except aiohttp.ClientError:
                # Ignore stations that raise ClientError
                continue

        return valid_full_stations
