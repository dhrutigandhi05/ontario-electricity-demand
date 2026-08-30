import pandas as pd
from sqlalchemy import text
from database import engine

DEMAND_FILE = "data/raw/ontario_demand_2025.csv"

def prepare_demand():
    df = pd.read_csv(
        DEMAND_FILE,
        skiprows=3,
    )

    df = df.rename(
        columns={
            "Date": "date",
            "Hour": "hour",
            "Market Demand": "market_demand",
            "Ontario Demand": "ontario_demand",
        }
    )

    df["date"] = pd.to_datetime(df["date"])

    df["hour"] = pd.to_numeric(
        df["hour"],
        errors="raise",
    )

    df["market_demand"] = pd.to_numeric(
        df["market_demand"],
        errors="raise",
    )

    df["ontario_demand"] = pd.to_numeric(
        df["ontario_demand"],
        errors="raise",
    )

    df = df.drop_duplicates(
        subset=["date", "hour"]
    )

    df["timestamp"] = (
        df["date"]
        + pd.to_timedelta(
            df["hour"] - 1,
            unit="h",
        )
    )

    df = (
        df.sort_values("timestamp")
        .reset_index(drop=True)
    )

    # Validation
    if df["timestamp"].isna().any():
        raise RuntimeError(
            "Demand data contains missing timestamps."
        )

    if df["ontario_demand"].isna().any():
        raise RuntimeError(
            "Demand data contains missing Ontario demand."
        )

    if df["timestamp"].duplicated().any():
        raise RuntimeError(
            "Demand data contains duplicate timestamps."
        )

    if not df["hour"].between(1, 24).all():
        raise RuntimeError(
            "Demand data contains invalid hour values."
        )

    return df[
        [
            "timestamp",
            "market_demand",
            "ontario_demand",
        ]
    ]

def load_demand():
    df = prepare_demand()

    records = df.to_dict(orient="records")

    query = text("""
        INSERT INTO demand_hourly (
            timestamp,
            market_demand,
            ontario_demand
        )
        VALUES (
            :timestamp,
            :market_demand,
            :ontario_demand
        )
        ON CONFLICT (timestamp)
        DO UPDATE SET
            market_demand = EXCLUDED.market_demand,
            ontario_demand = EXCLUDED.ontario_demand;
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            records,
        )

    print(f"Loaded {len(records)} demand observations.")

if __name__ == "__main__":
    load_demand()