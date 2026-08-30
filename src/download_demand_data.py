from pathlib import Path
import argparse
import urllib.request
import urllib.error

BASE_URL = "https://reports-public.ieso.ca/public/Demand"
DATA_DIR = Path("data/raw")

def get_url(year=None):
    if year is None:
        return f"{BASE_URL}/PUB_Demand.csv"

    return f"{BASE_URL}/PUB_Demand_{year}.csv"

def get_output_file(year=None):
    if year is None:
        return DATA_DIR / "ontario_demand_latest.csv"

    return DATA_DIR / f"ontario_demand_{year}.csv"

def download_data(year=None):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    url = get_url(year)
    output_file = get_output_file(year)

    if year is None:
        print("Downloading latest Ontario electricity demand data")
    else:
        print(f"Downloading Ontario electricity demand data for {year}")

    try:
        urllib.request.urlretrieve(url, output_file)

    except urllib.error.HTTPError as error:
        print(f"Could not download data: HTTP {error.code}")
        print(f"URL: {url}")
        return

    print(f"Saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Download Ontario electricity demand data from IESO."
    )

    parser.add_argument(
        "--year",
        type=int,
        help="Year of historical data to download"
    )

    args = parser.parse_args()
    download_data(args.year)

if __name__ == "__main__":
    main()