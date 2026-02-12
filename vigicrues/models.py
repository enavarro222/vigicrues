"""Pydantic models for Vigicrues API data structures."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ObservationType(str, Enum):
    """Type of observation: water level (H) or flow rate (Q)."""

    HEIGHT = "H"
    FLOW = "Q"


class Territory(BaseModel):
    """Represents a Vigicrues territory."""

    id: str = Field(..., description="Territory identifier")
    name: str = Field(..., description="Territory name")


class Troncon(BaseModel):
    """Represents a river section/segment within a territory."""

    id: str = Field(..., description="Troncon identifier")
    name: str = Field(..., description="Troncon name")


class Station(BaseModel):
    """Base model for a Vigicrues monitoring station."""

    id: str = Field(..., description="Station identifier")
    name: str = Field(..., description="Station name")


class StationDetails(Station):
    """Extended station information with additional details."""

    river: str = Field(..., description="Name of the river")
    city: str = Field(..., description="City where station is located")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    picture_url: Optional[str] = Field(
        None, description="URL to station photo (if available)"
    )
    commune_code: Optional[str] = Field(
        None, description="Commune code (if available)"
    )
    is_prediction_station: bool = Field(
        ..., description="Whether station provides predictions"
    )
    has_height_data: bool = Field(
        ..., description="Whether station has height observations"
    )
    has_flow_data: bool = Field(
        ..., description="Whether station has flow observations"
    )
    has_predictions: bool = Field(
        ..., description="Whether station has predictions"
    )
    historical_floods: List[Dict[str, Any]] = Field(
        ..., description="Historical flood data with name, height, and flow"
    )
    related_stations: List[Dict[str, Any]] = Field(
        ..., description="Related stations in same basin"
    )


class Observation(BaseModel):
    """A single data point for water level or flow."""

    timestamp: datetime = Field(..., description="Observation timestamp")
    value: float = Field(..., description="Observed value")
    type: ObservationType = Field(..., description="Type of observation")
    unit: str = Field(..., description="Unit of measurement (e.g., 'm' or 'm³/s')")


__all__ = [
    "ObservationType",
    "Territory",
    "Troncon",
    "Station",
    "StationDetails",
    "Observation",
]