from pathlib import Path
from datetime import datetime
import argparse
import json
import requests

STATIONS_API_URL = ("https://api.weather.gc.ca/collections/climate-stations/items")
HOURLY_API_URL = ("https://api.weather.gc.ca/collections/climate-hourly/items")
DATA_DIR = Path("data/raw")

def find_climate_id(year, tc_identifier):
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
    stations = data.get("features", [])

    if not stations:
        raise RuntimeError(
            f"No climate stations found for {tc_identifier}"
        )

    year_start = datetime(year, 1, 1)
    year_end = datetime(year, 12, 31)

    for station in stations:
        properties = station["properties"]
        first_date = properties.get("HLY_FIRST_DATE")
        last_date = properties.get("HLY_LAST_DATE")

        if not first_date:
            continue

        first_date = datetime.fromisoformat(
            first_date.replace("Z", "+00:00")
        ).replace(tzinfo=None)

        if last_date:
            last_date = datetime.fromisoformat(
                last_date.replace("Z", "+00:00")
            ).replace(tzinfo=None)
        else:
            last_date = datetime.max

        if first_date <= year_start and last_date >= year_end:
            climate_id = properties["CLIMATE_IDENTIFIER"]
            station_name = properties.get("STATION_NAME", "Unknown")

            print(
                f"Found station: {station_name} "
                f"(Climate ID {climate_id})"
            )

            return climate_id

    raise RuntimeError(
        f"No station for {tc_identifier} has hourly data "
        f"covering all of {year}"
    )

def download_station(year, name, tc_identifier):
    climate_id = find_climate_id(
        year=year,
        tc_identifier=tc_identifier,
    )

    output_file = (
        DATA_DIR /
        f"weather_{name}_{year}.json"
    )

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

    print(f"Downloading {name} weather data for {year}")

    response = requests.get(
        HOURLY_API_URL,
        params=params,
        timeout=60,
    )

    response.raise_for_status()
    data = response.json()
    observations = data.get("features", [])

    if not observations:
        raise RuntimeError(f"No hourly observations returned for {name}")

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file)

    print(f"Downloaded {len(observations)} observations")
    print(f"Saved to: {output_file}")

def download_weather(year, stations_file):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(stations_file, "r", encoding="utf-8") as file:
        stations = json.load(file)

    for station in stations:
        download_station(
            year=year,
            name=station["name"],
            tc_identifier=station["tc_identifier"],
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