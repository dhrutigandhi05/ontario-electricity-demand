from pathlib import Path
import json
import pandas as pd
from sqlalchemy import text
from database import engine

DATA_DIR = Path("data/raw")

STATIONS = [
    "toronto",
    "ottawa",
    "windsor",
    "sudbury",
    "thunder_bay",
]

YEAR = 2025

def prepare_weather():
    expected_hours = pd.date_range(
        f"{YEAR}-01-01 00:00:00",
        f"{YEAR}-12-31 23:00:00",
        freq="h",
    )

    frames = []

    for station in STATIONS:
        file_path = DATA_DIR / f"weather_{station}_{YEAR}.json"

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        df = pd.DataFrame(
            feature["properties"]
            for feature in data["features"]
        )

        df["timestamp"] = pd.to_datetime(df["LOCAL_DATE"])

        df["temperature"] = pd.to_numeric(
            df["TEMP"],
            errors="coerce",
        )

        df = (
            df[["timestamp", "temperature"]]
            .set_index("timestamp")
            .reindex(expected_hours)
        )

        df["temperature"] = df["temperature"].interpolate(
            method="time",
            limit=6,
            limit_area="inside",
        )

        df.index.name = "timestamp"
        df = df.reset_index()

        df["station"] = station

        frames.append(
            df[["timestamp", "station", "temperature"]]
        )

    weather = pd.concat(
        frames,
        ignore_index=True,
    )

    if weather["temperature"].isna().any():
        raise RuntimeError(
            "Weather data still contains missing temperatures."
        )

    if weather.duplicated(
        subset=["timestamp", "station"]
    ).any():
        raise RuntimeError(
            "Weather data contains duplicate timestamp/station pairs."
        )

    return weather

def load_weather():
    weather = prepare_weather()
    records = weather.to_dict(orient="records")

    query = text("""
        INSERT INTO weather_hourly (
            timestamp,
            station,
            temperature
        )
        VALUES (
            :timestamp,
            :station,
            :temperature
        )
        ON CONFLICT (timestamp, station)
        DO UPDATE SET
            temperature = EXCLUDED.temperature;
    """)

    with engine.begin() as connection:
        connection.execute(query, records)

    print(f"Loaded {len(records)} weather observations.")

if __name__ == "__main__":
    load_weather()