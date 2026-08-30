from pathlib import Path
from datetime import datetime
import argparse
import json
import requests

STATIONS_API_URL = ("https://api.weather.gc.ca/collections/climate-stations/items")
HOURLY_API_URL = ("https://api.weather.gc.ca/collections/climate-hourly/items")
DATA_DIR = Path("data/raw")

def expected_hours_in_year(year):
    start = datetime(year, 1, 1)
    end = datetime(year + 1, 1, 1)
    return int((end - start).total_seconds() / 3600)

def find_station_candidates(tc_identifiers):
    candidates = {}

    for tc_identifier in tc_identifiers:
        station_filter = (
            f"properties.TC_IDENTIFIER = '{tc_identifier}'"
        )

        params = {
            "f": "json",
            "lang": "en",
            "limit": 1000,
            "filter": station_filter,
        }

        response = requests.get(
            STATIONS_API_URL,
            params=params,
            timeout=60,
        )

        response.raise_for_status()
        data = response.json()

        for feature in data.get("features", []):
            properties = feature["properties"]
            climate_id = properties.get("CLIMATE_IDENTIFIER")

            if not climate_id:
                continue

            candidates[climate_id] = {
                "climate_id": climate_id,
                "station_name": properties.get(
                    "STATION_NAME",
                    "Unknown",
                ),
                "tc_identifier": tc_identifier,
            }

    return list(candidates.values())

def get_hourly_data(year, climate_id):
    weather_filter = (
        f"properties.CLIMATE_IDENTIFIER = '{climate_id}' "
        f"AND properties.LOCAL_YEAR = {year}"
    )

    params = {
        "f": "json",
        "lang": "en",
        "limit": 10000,
        "filter": weather_filter,
    }

    response = requests.get(
        HOURLY_API_URL,
        params=params,
        timeout=60,
    )

    response.raise_for_status()
    return response.json()

def find_best_station(year, tc_identifiers):
    candidates = find_station_candidates(tc_identifiers)

    if not candidates:
        raise RuntimeError(
            f"No climate stations found for {tc_identifiers}"
        )

    best_candidate = None
    best_data = None
    best_count = -1

    print("Checking candidate stations...")

    for candidate in candidates:
        climate_id = candidate["climate_id"]

        data = get_hourly_data(
            year=year,
            climate_id=climate_id,
        )

        observation_count = len(
            data.get("features", [])
        )

        print(
            f"  {candidate['station_name']} "
            f"(Climate ID {climate_id}): "
            f"{observation_count} observations"
        )

        if observation_count > best_count:
            best_count = observation_count
            best_candidate = candidate
            best_data = data

    return best_candidate, best_data, best_count

def download_station(year, name, tc_identifiers):
    expected_hours = expected_hours_in_year(year)

    candidate, data, observation_count = find_best_station(
        year=year,
        tc_identifiers=tc_identifiers,
    )

    if observation_count == 0:
        raise RuntimeError(
            f"No hourly observations found for {name} in {year}"
        )

    coverage = observation_count / expected_hours * 100

    print(
        f"Selected: {candidate['station_name']} "
        f"(Climate ID {candidate['climate_id']})"
    )

    print(
        f"Coverage: {observation_count}/{expected_hours} "
        f"hours ({coverage:.2f}%)"
    )

    if observation_count < expected_hours:
        print(
            f"Warning: {name} is missing "
            f"{expected_hours - observation_count} hourly observations."
        )

    output_file = DATA_DIR / f"weather_{name}_{year}.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file)

    print(f"Saved to: {output_file}")

def download_weather(year, stations_file):
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        stations_file,
        "r",
        encoding="utf-8",
    ) as file:
        stations = json.load(file)

    for station in stations:
        print(f"\n{station['name']}")
        tc_identifiers = station.get("tc_identifiers")

        if tc_identifiers is None:
            tc_identifiers = [
                station["tc_identifier"]
            ]

        download_station(
            year=year,
            name=station["name"],
            tc_identifiers=tc_identifiers,
        )

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Download hourly Ontario weather data "
            "from Environment Canada."
        )
    )

    parser.add_argument(
        "--year",
        type=int,
        required=True,
        help="Year to download",
    )

    parser.add_argument(
        "--stations-file",
        default="config/weather_stations.json",
        help="Weather station configuration file",
    )

    args = parser.parse_args()

    download_weather(
        year=args.year,
        stations_file=args.stations_file,
    )

if __name__ == "__main__":
    main()