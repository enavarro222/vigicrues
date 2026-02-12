# Vigicrues Python Client

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![PyPI](https://img.shields.io/pypi/v/vigicrues.svg)](https://pypi.org/project/vigicrues/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/enavarro222/vigicrues/blob/main/LICENSE)
[![Code Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/enavarro222/vigicrues)

A Python client for the Vigicrues API (French flood monitoring service). This library allows you to search for monitoring stations and retrieve real-time water level and flow rate observations.

## Features

- **Search Stations**: Find monitoring stations using the OpenDataSoft API
- **Station Details**: Get comprehensive information about specific stations
- **Real-time Observations**: Retrieve latest water level (H) and flow rate (Q) data
- **Territory Management**: List territories and river sections
- **CLI Interface**: Command-line tool for quick data access
- **Async Support**: Fully asynchronous implementation for high performance

## Installation

```bash
pip install vigicrues
```

Or install from source:

```bash
git clone git@github.com:enavarro222/vigicrues.git
cd vigicrues
pip install -e .[dev]
```

## Quick Start

```python
import asyncio
from vigicrues import Vigicrues

async def main():
    # Initialize client
    async with Vigicrues() as client:
        # Search for stations
        stations = await client.search_stations("Paris")
        print(f"Found {len(stations)} stations:")
        for station in stations:
            print(f"- {station.name} (ID: {station.id})")

        # Get station details
        if stations:
            details = await client.get_station_details(stations[0].id)
            print(f"\nStation details for {details.name}:")
            print(f"  River: {details.river}")
            print(f"  Location: {details.city}")
            print(f"  Coordinates: ({details.latitude}, {details.longitude})")

            # Get latest observations
            if details.has_height_data:
                observation = await client.get_latest_observations(details.id, "H")
                print(f"  Latest water level: {observation.value} {observation.unit} at {observation.timestamp}")

            if details.has_flow_data:
                observation = await client.get_latest_observations(details.id, "Q")
                print(f"  Latest flow rate: {observation.value} {observation.unit} at {observation.timestamp}")

if __name__ == "__main__":
    asyncio.run(main())
```

## CLI Usage

```bash
# Search for stations
vigicrues search "Paris"

# Get latest observations for a station
vigicrues get O408101001

# List all territories
vigicrues territories

# List troncons in a territory
vigicrues troncons 25

# List stations in a troncon
vigicrues stations TL12
```

## API Documentation

### Client Initialization

The `Vigicrues` client supports two initialization patterns:

#### Pattern 1: Async Context Manager (Recommended)

```python
async with Vigicrues() as client:
    # Use client here
    pass
# Session automatically closed
```

#### Pattern 2: External Session (Advanced)

```python
async with aiohttp.ClientSession() as session:
    client = Vigicrues(session=session)
    # Use client here
# User responsible for closing session
```

### Main Client Methods

#### Search Stations

```python
async def search_stations(self, query: str) -> list[Station]:
    """Search for stations by name or location.

    Args:
        query: Search term (station name, city, etc.)

    Returns:
        List of matching stations
    """
```

#### Get Station Details

```python
async def get_station_details(self, station_id: str) -> StationDetails:
    """Get comprehensive details for a specific station.

    Args:
        station_id: Station identifier (e.g., "O408101001")

    Returns:
        Detailed station information including location, historical floods, etc.
    """
```

#### Get Latest Observations

```python
async def get_latest_observations(self, station_id: str, obs_type: str) -> Observation:
    """Get the latest observation for a station.

    Args:
        station_id: Station identifier
        obs_type: Observation type ("H" for height, "Q" for flow)

    Returns:
        Latest observation with timestamp
    """
```

### Data Models

#### Territory

Represents a Vigicrues territory.

- `id`: `str` (e.g., "25")
- `name`: `str` (e.g., "Garonne-Tarn-Lot")

#### Troncon

Represents a river section/segment within a territory.

- `id`: `str` (e.g., "TL12")
- `name`: `str` (e.g., "Célé")

#### Station

Base model for a Vigicrues monitoring station.

- `id`: `str` (e.g., "O494101001")
- `name`: `str`

#### StationDetails

Extends Station with additional detailed information.

- `river`: `str`
- `city`: `str`
- `latitude`: `float`
- `longitude`: `float`
- `picture_url`: `str | None`
- `commune_code`: `str | None`
- `is_prediction_station`: `bool`
- `has_height_data`: `bool`
- `has_flow_data`: `bool`
- `has_predictions`: `bool`
- `historical_floods`: `list[dict]`
- `related_stations`: `list[dict]`

#### Observation

A single data point for water level or flow.

- `timestamp`: `datetime`
- `value`: `float`
- `type`: `ObservationType` (Enum: `H` for Height, `Q` for Flow)
- `unit`: `str` (e.g., "m" or "m³/s")

## Development

### Requirements

- Python 3.10+
- `aiohttp` for HTTP requests
- `pydantic` for data validation
- `ruff` for linting and formatting
- `mypy` for type checking
- `pytest` for testing

### Running Tests

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests with coverage
pytest --cov=vigicrues --cov-report=html

# Run linting and type checking
ruff check vigicrues tests
mypy vigicrues
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## API Sources

This client uses the following official Vigicrues APIs:

- **OpenDataSoft API**: Station metadata and search
- **Vigicrues API**: Real-time observations and station details

## Support

For issues and questions, please open an issue on the [GitHub repository](https://github.com/enavarro222/vigicrues).
