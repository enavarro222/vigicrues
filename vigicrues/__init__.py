"""Modern asynchronous Python client for the Vigicrues API (French flood monitoring service)."""
from .client import Vigicrues
from .discovery import DiscoveryClient
from .vigicrues import VigicruesClient
from .models import (
    Territory,
    Troncon,
    Station,
    StationDetails,
    Observation,
    ObservationType,
)

__version__ = "0.1.0"
__all__ = [
    "Vigicrues",
    "DiscoveryClient",
    "VigicruesClient",
    "Territory",
    "Troncon",
    "Station",
    "StationDetails",
    "Observation",
    "ObservationType",
]