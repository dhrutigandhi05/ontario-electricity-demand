from pathlib import Path
import argparse
import requests

API_URL = "https://api.weather.gc.ca/collections/climate-hourly/items"
DATA_DIR = Path("data/raw")

def download_weather(year, climate_id):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_file = DATA_DIR / f"weather_{climate_id}_{year}.csv"

    weather_filter = (
        f"properties.CLIMATE_IDENTIFIER = '{climate_id}' "
        f"AND properties.LOCAL_YEAR = {year}"
    )

    params = {
        "f": "csv",
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
    output_file.write_bytes(response.content)
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