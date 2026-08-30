import pandas as pd
from sqlalchemy import text
from database import engine

DEMAND_FILE = "data/processed/ontario_demand_2025_clean.csv"

def load_demand():
    df = pd.read_csv(DEMAND_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    records = df[
        ["timestamp", "market_demand", "ontario_demand"]
    ].to_dict(orient="records")

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
        connection.execute(query, records)

    print(f"Loaded {len(records)} demand observations")

if __name__ == "__main__":
    load_demand()