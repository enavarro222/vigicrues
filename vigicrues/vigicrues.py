"""VigicruesClient for accessing Vigicrues API endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import List, Tuple, Dict

import aiohttp
import pyproj

from .models import (
    Observation,
    ObservationType,
    Station,
    StationDetails,
    Territory,
    Troncon,
)


class VigicruesClient:
    """Client for accessing Vigicrues API endpoints."""

    VIGICRUES_BASE_URL = "https://www.vigicrues.gouv.fr/services"
    TRANSFORMER = pyproj.Transformer.from_crs("EPSG:2154", "EPSG:4326", always_xy=True)

    def __init__(self, session: aiohttp.ClientSession | None = None) -> None:
        """Initialize VigicruesClient.

        Args:
            session: aiohttp session.
        """
        self._session = session

    async def get_territories(self) -> List[Territory]:
        """Get list of all territories.

        Returns:
            List of territories

        Raises:
            aiohttp.ClientError: For HTTP errors
            json.JSONDecodeError: If response is not valid JSON
            ValidationError: If response data is invalid
        """
        if self._session is None:
            raise RuntimeError("Session is not initialized")
        async with self._session.get(
            f"{self.VIGICRUES_BASE_URL}/TerEntVigiCru.json"
        ) as response:
            response.raise_for_status()
            data = await response.json()

            territories = []
            for territory_data in data.get("ListEntVigiCru", []):
                territories.append(
                    Territory(
                        id=territory_data.get("CdEntVigiCru"),
                        name=territory_data.get("LbEntVigiCru"),
                    )
                )

            return territories

    async def get_troncons(self, territory_id: str) -> List[Troncon]:
        """Get list of troncons for a specific territory.

        Args:
            territory_id: Territory identifier

        Returns:
            List of troncons

        Raises:
            ValueError: If territory_id is empty
            aiohttp.ClientError: For HTTP errors
            json.JSONDecodeError: If response is not valid JSON
            ValidationError: If response data is invalid
        """
        if not territory_id:
            raise ValueError("Territory ID cannot be empty")

        url = f"{self.VIGICRUES_BASE_URL}/v1.1/TerEntVigiCru.json"
        params = {"CdEntVigiCru": territory_id, "TypEntVigiCru": "5"}

        if self._session is None:
            raise RuntimeError("Session is not initialized")
        async with self._session.get(url, params=params) as response:
            response.raise_for_status()
            data = await response.json()

            troncons = []
            for territory_data in data.get("ListEntVigiCru", []):
                for troncon_data in territory_data.get("aNMoinsUn", []):
                    troncons.append(
                        Troncon(
                            id=troncon_data.get("CdEntVigiCruInferieur"),
                            name=troncon_data.get("LbEntVigiCruInferieur"),
                        )
                    )

            return troncons

    async def get_troncon_stations(self, troncon_id: str) -> List[Station]:
        """Get list of stations for a specific troncon.

        Args:
            troncon_id: Troncon identifier

        Returns:
            List of stations

        Raises:
            ValueError: If troncon_id is empty
            aiohttp.ClientError: For HTTP errors
            json.JSONDecodeError: If response is not valid JSON
            ValidationError: If response data is invalid
        """
        if not troncon_id:
            raise ValueError("Troncon ID cannot be empty")

        url = f"{self.VIGICRUES_BASE_URL}/v1.1/TronEntVigiCru.json"
        params = {"CdEntVigiCru": troncon_id, "TypEntVigiCru": "8"}

        if self._session is None:
            raise RuntimeError("Session is not initialized")
        async with self._session.get(url, params=params) as response:
            response.raise_for_status()
            data = await response.json()

            stations = []
            for territory_data in data.get("ListEntVigiCru", []):
                for station_data in territory_data.get("aNMoinsUn", []):
                    stations.append(
                        Station(
                            id=station_data.get("CdEntVigiCruInferieur"),
                            name=station_data.get("LbEntVigiCruInferieur"),
                        )
                    )

            return stations

    @classmethod
    def extract_coordinates(
        cls, coord_data: Dict[str, str], station_id: str
    ) -> Tuple[float, float]:
        """Extract and convert coordinates from station data.

        >>> VigicruesClient.extract_coordinates({
        ...     "CoordXStationHydro": "567613",
        ...     "CoordYStationHydro": "6325598",
        ... }, station_id="O494101001")
        (44.016925576..., 1.348806124...)

        >>> VigicruesClient.extract_coordinates({
        ...     "CoordXStationHydro": "",
        ...     "CoordYStationHydro": "6325598",
        ... }, station_id="O494101001")
        Traceback (most recent call last):
        ...
        ValueError: Missing coordinates for station O494101001

        >>> VigicruesClient.extract_coordinates({
        ...     "CoordXStationHydro": None,
        ...     "CoordYStationHydro": "6325598",
        ... }, station_id="O494101001")
        Traceback (most recent call last):
        ...
        ValueError: Missing coordinates for station O494101001

        >>> VigicruesClient.extract_coordinates({
        ...     "CoordXStationHydro": "abc",
        ...     "CoordYStationHydro": "6325598",
        ... }, station_id="O494101001")
        Traceback (most recent call last):
        ...
        ValueError: Invalid coordinate format: abc, 6325598
        """
        # Get Lambert 93 coordinates
        x_str = coord_data.get("CoordXStationHydro")
        y_str = coord_data.get("CoordYStationHydro")
        if not x_str or not y_str:
            raise ValueError(f"Missing coordinates for station {station_id}")

        # Convert to float and validate
        try:
            x = float(x_str)
            y = float(y_str)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid coordinate format: {x_str}, {y_str}")

        # Convert to WGS84
        longitude, latitude = cls.TRANSFORMER.transform(x, y)
        return latitude, longitude

    async def get_station_details(self, station_id: str) -> StationDetails:
        """Get comprehensive details for a specific station.

        Args:
            station_id: Station identifier

        Returns:
            Detailed station information with WGS84 coordinates

        Raises:
            ValueError: If station_id is empty or coordinates are invalid
            aiohttp.ClientError: For HTTP errors
            json.JSONDecodeError: If response is not valid JSON
            ValidationError: If response data is invalid
        """
        if not station_id:
            raise ValueError("Station ID cannot be empty")

        url = f"{self.VIGICRUES_BASE_URL}/station.json/index.php"
        params = {"CdStationHydro": station_id}

        if self._session is None:
            raise RuntimeError("Session is not initialized")
        async with self._session.get(url, params=params) as response:
            response.raise_for_status()
            data = await response.json()

            station_data = data.get("VigilanceCrues", {})
            coord_data = data.get("CoordStationHydro", {})
            latitude, longitude = self.extract_coordinates(
                coord_data, station_id=station_id
            )

            return StationDetails(
                id=station_id,
                name=data.get("LbStationHydro"),
                river=data.get("LbCoursEau"),
                city=data.get("CdCommune"),
                latitude=latitude,
                longitude=longitude,
                picture_url=station_data.get("Photo"),
                commune_code=data.get("CdCommune"),
                is_prediction_station=station_data.get("StationPrevision", False),
                has_height_data=True,  # Assume height data is available
                has_flow_data=True,  # Assume flow data is available
                has_predictions=station_data.get("StationPrevision", False),
                historical_floods=station_data.get("CruesHistoriques", []),
                related_stations=station_data.get("StationsBassin", []),
            )

    async def get_latest_observations(
        self, station_id: str, obs_type: str
    ) -> Observation:
        """Get the latest observation for a station.

        Args:
            station_id: Station identifier
            obs_type: Observation type ("H" for height, "Q" for flow)

        Returns:
            Latest observation

        Raises:
            ValueError: If station_id is empty or obs_type is invalid
            aiohttp.ClientError: For HTTP errors
            json.JSONDecodeError: If response is not valid JSON
            ValidationError: If response data is invalid
        """
        if not station_id:
            raise ValueError("Station ID cannot be empty")
        if obs_type not in ["H", "Q"]:
            raise ValueError("obs_type must be 'H' (height) or 'Q' (flow)")

        url = f"{self.VIGICRUES_BASE_URL}/observations.json/index.php"
        params = {
            "CdStationHydro": station_id,
            "GrdSerie": obs_type,
            "FormatDate": "iso",
        }

        if self._session is None:
            raise RuntimeError("Session is not initialized")
        async with self._session.get(url, params=params) as response:
            response.raise_for_status()
            data = await response.json()

            observations = data.get("Serie", {}).get("ObssHydro", [])
            if not observations:
                raise ValueError("No observations found")

            # Get the latest observation (last in the list)
            latest_observation = observations[-1]

            return Observation(
                timestamp=datetime.fromisoformat(latest_observation.get("DtObsHydro")),
                value=latest_observation.get("ResObsHydro"),
                type=ObservationType(obs_type),
                unit="m" if obs_type == "H" else "m³/s",
            )
