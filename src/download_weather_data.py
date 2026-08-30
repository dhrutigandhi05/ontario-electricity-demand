from pathlib import Path
import argparse
import json
import requests

API_URL = "https://api.weather.gc.ca/collections/climate-hourly/items"
DATA_DIR = Path("data/raw")

def download_weather(year, climate_id):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_file = DATA_DIR / f"weather_{climate_id}_{year}.json"

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

    print(
        f"Downloading weather data for station {climate_id}, year {year}"
    )

    response = requests.get(
        API_URL,
        params=params,
        timeout=60,
    )

    response.raise_for_status()
    data = response.json()
    features = data.get("features", [])

    if not features:
        raise RuntimeError(
            "The API returned 0 weather observations. "
            "Check the climate ID and year."
        )

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file)

    print(f"Downloaded {len(features)} observations")
    print(f"Saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Download hourly weather data from Environment Canada."
    )

    parser.add_argument(
        "--year",
        type=int,
        required=True,
        help="Year to download",
    )

    parser.add_argument(
        "--climate-id",
        required=True,
        help="Environment Canada climate station ID",
    )

    args = parser.parse_args()

    download_weather(
        year=args.year,
        climate_id=args.climate_id,
    )

if __name__ == "__main__":
    main()