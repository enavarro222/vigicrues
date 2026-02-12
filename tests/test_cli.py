"""Tests for CLI commands."""
import argparse
from datetime import datetime

from unittest.mock import patch

import pytest

from vigicrues import Vigicrues
from vigicrues.models import (
    Station,
    StationDetails,
    Observation,
    ObservationType,
    Territory,
    Troncon
)
from vigicrues import cli


@pytest.fixture
def mock_args() -> argparse.Namespace:
    """Fixture for mock argparse arguments."""
    return argparse.Namespace()

@pytest.fixture
def mock_vigicrues_client() -> Vigicrues:
    with patch("vigicrues.cli.Vigicrues") as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value
        yield mock_instance


@pytest.mark.asyncio
async def test_search_command(mock_args: argparse.Namespace, mock_vigicrues_client) -> None:
    """Test search CLI command."""
    mock_args.query = "Sulpice"
    mock_args.func = cli.search

    mock_vigicrues_client.search_stations.return_value = [
        Station(id="O408101001", name="Le Tarn à Rabastens - Saint-Sulpice")
    ]

    await cli.run(mock_args)

    mock_vigicrues_client.search_stations.assert_called_once_with("Sulpice")


@pytest.mark.asyncio
async def test_search_command_not_found(mock_args: argparse.Namespace, mock_vigicrues_client) -> None:
    """Test search CLI command no results."""
    mock_args.query = "Sulpice"
    mock_args.func = cli.search

    mock_vigicrues_client.search_stations.return_value = []

    await cli.run(mock_args)

    mock_vigicrues_client.search_stations.assert_called_once_with("Sulpice")


@pytest.mark.asyncio
async def test_get_command_with_height_data(mock_args: argparse.Namespace, mock_vigicrues_client) -> None:
    """Test get CLI command with height data."""
    mock_args.station_id = "O408101001"
    mock_args.func = cli.get

    mock_vigicrues_client.get_station_details.return_value = StationDetails(
        id="O408101001",
        name="Le Tarn à Rabastens - Saint-Sulpice",
        river="Le Tarn",
        city="Rabastens",
        latitude=43.823,
        longitude=1.726,
        has_height_data=True,
        has_flow_data=False,
        picture_url=None,
        commune_code=None,
        is_prediction_station=False,
        has_predictions=False,
        historical_floods=[],
        related_stations=[]
    )
    mock_vigicrues_client.get_latest_observations.return_value = Observation(
        value=2.5,
        unit="m",
        type=ObservationType.HEIGHT,
        timestamp=datetime(2024, 1, 1, 12, 0, 0)
    )

    await cli.run(mock_args)

    mock_vigicrues_client.get_station_details.assert_called_once_with("O408101001")
    mock_vigicrues_client.get_latest_observations.assert_called_once_with("O408101001", "H")


@pytest.mark.asyncio
async def test_get_command_with_flow_data(mock_args: argparse.Namespace, mock_vigicrues_client) -> None:
    """Test get CLI command with flow data."""
    mock_args.station_id = "O408101001"
    mock_args.func = cli.get

    mock_vigicrues_client.get_station_details.return_value = StationDetails(
        id="O408101001",
        name="Le Tarn à Rabastens - Saint-Sulpice",
        river="Le Tarn",
        city="Rabastens",
        latitude=43.823,
        longitude=1.726,
        has_height_data=False,
        has_flow_data=True,
        picture_url=None,
        commune_code=None,
        is_prediction_station=False,
        has_predictions=False,
        historical_floods=[],
        related_stations=[]
    )
    mock_vigicrues_client.get_latest_observations.return_value = Observation(
        value=150.0,
        unit="m3/s",
        type=ObservationType.FLOW,
        timestamp=datetime(2024, 1, 1, 12, 0, 0)
    )

    await cli.run(mock_args)

    mock_vigicrues_client.get_station_details.assert_called_once_with("O408101001")
    mock_vigicrues_client.get_latest_observations.assert_called_once_with("O408101001", "Q")


@pytest.mark.asyncio
async def test_get_command_with_both_data(mock_args: argparse.Namespace, mock_vigicrues_client) -> None:
    """Test get CLI command with both height and flow data."""
    mock_args.station_id = "O408101001"
    mock_args.func = cli.get

    mock_vigicrues_client.get_station_details.return_value = StationDetails(
        id="O408101001",
        name="Le Tarn à Rabastens - Saint-Sulpice",
        river="Le Tarn",
        city="Rabastens",
        latitude=43.823,
        longitude=1.726,
        has_height_data=True,
        has_flow_data=True,
        picture_url=None,
        commune_code=None,
        is_prediction_station=False,
        has_predictions=False,
        historical_floods=[],
        related_stations=[]
    )
    mock_vigicrues_client.get_latest_observations.side_effect = [
        Observation(value=2.5, unit="m", type=ObservationType.HEIGHT, timestamp=datetime(2024, 1, 1, 12, 0, 0)),
        Observation(value=150.0, unit="m3/s", type=ObservationType.FLOW, timestamp=datetime(2024, 1, 1, 12, 0, 0))
    ]

    await cli.run(mock_args)

    mock_vigicrues_client.get_station_details.assert_called_once_with("O408101001")
    assert mock_vigicrues_client.get_latest_observations.call_count == 2
    mock_vigicrues_client.get_latest_observations.assert_any_call("O408101001", "H")
    mock_vigicrues_client.get_latest_observations.assert_any_call("O408101001", "Q")


@pytest.mark.asyncio
async def test_territories_command(mock_args: argparse.Namespace, mock_vigicrues_client) -> None:
    """Test territories CLI command."""
    mock_args = argparse.Namespace()
    mock_args.func = cli.territories

    mock_vigicrues_client.get_territories.return_value = [
        Territory(id="25", name="Garonne-Tarn-Lot"),
        Territory(id="26", name="Rhône-Méditerranée")
    ]

    await cli.run(mock_args)

    mock_vigicrues_client.get_territories.assert_called_once()


@pytest.mark.asyncio
async def test_territories_command_no_results(mock_args: argparse.Namespace, mock_vigicrues_client) -> None:
    """Test territories CLI command when no results are returned."""
    mock_args = argparse.Namespace()
    mock_args.func = cli.territories

    mock_vigicrues_client.get_territories.return_value = []

    await cli.run(mock_args)


@pytest.mark.asyncio
async def test_troncons_command(mock_args: argparse.Namespace, mock_vigicrues_client) -> None:
    """Test troncons CLI command."""
    mock_args.territory_id = "25"
    mock_args.func = cli.troncons

    mock_vigicrues_client.get_troncons.return_value = [
        Troncon(id="1", name="Tarn amont"),
        Troncon(id="2", name="Tarn aval")
    ]

    await cli.run(mock_args)

    mock_vigicrues_client.get_troncons.assert_called_once_with("25")


@pytest.mark.asyncio
async def test_troncons_command_no_results(mock_args: argparse.Namespace, mock_vigicrues_client) -> None:
    """Test troncons CLI command."""
    mock_args.territory_id = "254"
    mock_args.func = cli.troncons

    mock_vigicrues_client.get_troncons.return_value = []
    await cli.run(mock_args)


@pytest.mark.asyncio
async def test_stations_command(mock_args: argparse.Namespace, mock_vigicrues_client) -> None:
    """Test stations CLI command."""
    mock_args.troncon_id = "1"
    mock_args.func = cli.stations

    mock_vigicrues_client.get_troncon_stations.return_value = [
        Station(id="O408101001", name="Le Tarn à Rabastens - Saint-Sulpice"),
        Station(id="O408101002", name="Le Tarn à Albi")
    ]

    await cli.run(mock_args)

    mock_vigicrues_client.get_troncon_stations.assert_called_once_with("1")


@pytest.mark.asyncio
async def test_stations_command_no_results(mock_args: argparse.Namespace, mock_vigicrues_client) -> None:
    """Test stations CLI command when no results are returned."""
    mock_args.troncon_id = "1"
    mock_args.func = cli.stations

    mock_vigicrues_client.get_troncon_stations.return_value = []

    await cli.run(mock_args)


@pytest.mark.asyncio
async def test_main_command_line_interface() -> None:
    """Test main CLI entry point with different commands."""
    # Test search command
    with patch("vigicrues.cli.argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(
        command="search",
        query="Sulpice",
        func=cli.search
    )), patch("vigicrues.cli.asyncio.run") as mock_run:
        cli.main()
        mock_run.assert_called_once()

    # Test get command
    with patch("vigicrues.cli.argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(
        command="get",
        station_id="O408101001",
        func=cli.get
    )), patch("vigicrues.cli.asyncio.run") as mock_run:
        cli.main()
        mock_run.assert_called_once()

    # Test territories command
    with patch("vigicrues.cli.argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(
        command="territories",
        func=cli.territories
    )), patch("vigicrues.cli.asyncio.run") as mock_run:
        cli.main()
        mock_run.assert_called_once()

    # Test troncons command
    with patch("vigicrues.cli.argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(
        command="troncons",
        territory_id="25",
        func=cli.troncons
    )), patch("vigicrues.cli.asyncio.run") as mock_run:
        cli.main()
        mock_run.assert_called_once()

    # Test stations command
    with patch("vigicrues.cli.argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(
        command="stations",
        troncon_id="1",
        func=cli.stations
    )), patch("vigicrues.cli.asyncio.run") as mock_run:
        cli.main()
        mock_run.assert_called_once()
