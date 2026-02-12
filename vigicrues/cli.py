"""Command-line interface for Vigicrues client."""
import argparse
import asyncio
from typing import Any

from .client import Vigicrues


async def search(client: Vigicrues, args: Any) -> None:
    """Search for stations."""
    stations = await client.search_stations(args.query)
    if stations:
        print(f"Found {len(stations)} stations:")
        for station in stations:
            print(f"  {station.name} (ID: {station.id})")
    else:
        print("No stations found")


async def get(client: Vigicrues, args: Any) -> None:
    """Get latest observations for a station."""
    details = await client.get_station_details(args.station_id)
    print(f"Station: {details.name}")
    print(f"River: {details.river}")
    print(f"City: {details.city}")
    print(f"Coordinates: ({details.latitude}, {details.longitude})")

    if details.has_height_data:
        observation = await client.get_latest_observations(details.id, "H")
        print(f"\nLatest water level: {observation.value} {observation.unit} at {observation.timestamp}")

    if details.has_flow_data:
        observation = await client.get_latest_observations(details.id, "Q")
        print(f"Latest flow rate: {observation.value} {observation.unit} at {observation.timestamp}")


async def territories(client: Vigicrues, args: Any) -> None:
    """List all territories."""
    territories = await client.get_territories()
    if territories:
        print("Territories:")
        for territory in territories:
            print(f"  - {territory.name} (id: {territory.id})")
    else:
        print("No territories found")


async def troncons(client: Vigicrues, args: Any) -> None:
    """List troncons in a territory."""
    troncons = await client.get_troncons(args.territory_id)
    if troncons:
        print(f"Troncons in territory {args.territory_id}:")
        for troncon in troncons:
            print(f"  - {troncon.name} (id: {troncon.id})")
    else:
        print("No troncons found")


async def stations(client: Vigicrues, args: Any) -> None:
    """List stations in a troncon."""
    stations = await client.get_troncon_stations(args.troncon_id)
    if stations:
        print(f"Stations in troncon {args.troncon_id}:")
        for station in stations:
            print(f"  - {station.name} (id: {station.id})")
    else:
        print("No stations found")


async def run(args: argparse.Namespace) -> None:
    """Run an async function with given arguments."""
    async with Vigicrues() as client:
        await args.func(client, args)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Vigicrues CLI - French flood monitoring service"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for stations")
    search_parser.add_argument("query", help="Search term (station name, city, etc.)")
    search_parser.set_defaults(func=search)

    # Get command
    get_parser = subparsers.add_parser("get", help="Get latest observations for a station")
    get_parser.add_argument("station_id", help="Station identifier (e.g., O408101001)")
    get_parser.set_defaults(func=get)

    # Territories command
    territories_parser = subparsers.add_parser("territories", help="List all territories")
    territories_parser.set_defaults(func=territories)

    # Troncons command
    troncons_parser = subparsers.add_parser("troncons", help="List troncons in a territory")
    troncons_parser.add_argument("territory_id", help="Territory identifier")
    troncons_parser.set_defaults(func=troncons)

    # Stations command
    stations_parser = subparsers.add_parser("stations", help="List stations in a troncon")
    stations_parser.add_argument("troncon_id", help="Troncon identifier")
    stations_parser.set_defaults(func=stations)

    args = parser.parse_args()
    asyncio.run(run(args))
    
if __name__ == "__main__":
    main()