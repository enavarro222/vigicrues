"""Main Vigicrues client combining DiscoveryClient and VigicruesClient."""
from __future__ import annotations

import aiohttp

from .discovery import DiscoveryClient
from .vigicrues import VigicruesClient


class Vigicrues(VigicruesClient, DiscoveryClient):
    """Combined client for Vigicrues and station discovery."""

    def __init__(self, session: aiohttp.ClientSession | None = None, timeout: float | None = None) -> None:
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
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self._timeout))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context, closing session only if we own it."""
        if self._owns_session and self._session:
            await self._session.close()