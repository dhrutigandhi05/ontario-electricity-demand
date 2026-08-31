from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from database import engine

MODEL_DIR = Path("models")
MODEL_FILE = MODEL_DIR / "ontario_demand_model.joblib"
BASE_TEMP = 18

def load_data():
    query = """
    SELECT
        d.timestamp,
        d.ontario_demand,

        MAX(CASE
            WHEN w.station = 'toronto'
            THEN w.temperature
        END) AS toronto_temp,

        MAX(CASE
            WHEN w.station = 'ottawa'
            THEN w.temperature
        END) AS ottawa_temp,

        MAX(CASE
            WHEN w.station = 'windsor'
            THEN w.temperature
        END) AS windsor_temp,

        MAX(CASE
            WHEN w.station = 'sudbury'
            THEN w.temperature
        END) AS sudbury_temp,

        MAX(CASE
            WHEN w.station = 'thunder_bay'
            THEN w.temperature
        END) AS thunder_bay_temp

    FROM demand_hourly d

    JOIN weather_hourly w
        ON d.timestamp = w.timestamp

    GROUP BY
        d.timestamp,
        d.ontario_demand

    ORDER BY d.timestamp;
    """

    df = pd.read_sql(query, engine)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

def create_features(df):
    df = df.copy()
    df["hour"] = df["timestamp"].dt.hour # time of day
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["day_of_week"] = df["timestamp"].dt.day_name() # day of week

    day_columns = pd.get_dummies(
        df["day_of_week"],
        prefix="day",
        dtype=int,
        drop_first=True,
    )

    df = pd.concat(
        [df, day_columns],
        axis=1,
    )

    # weather
    weather_features = [
        "toronto_temp",
        "ottawa_temp",
        "windsor_temp",
        "sudbury_temp",
        "thunder_bay_temp",
    ]

    df["avg_temp"] = df[weather_features].mean(axis=1)

    # heating / cooling
    df["heating"] = np.maximum(
        BASE_TEMP - df["avg_temp"],
        0,
    )

    df["cooling"] = np.maximum(
        df["avg_temp"] - BASE_TEMP,
        0,
    )

    feature_columns = (
        ["hour_sin", "hour_cos"]
        + day_columns.columns.tolist()
        + weather_features
        + ["heating", "cooling"]
    )

    X = df[feature_columns]
    y = df["ontario_demand"]
    return X, y, feature_columns

def train_model():
    df = load_data()
    X, y, feature_columns = create_features(df)
    split_index = int(len(df) * 0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    model = LinearRegression()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    mse = mean_squared_error(
        y_test,
        predictions,
    )

    rmse = mse ** 0.5

    print(f"Training rows: {len(X_train)}")
    print(f"Testing rows: {len(X_test)}")
    print(f"MSE: {mse:.2f}")
    print(f"RMSE: {rmse:.2f} MW")

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_data = {
        "model": model,
        "features": feature_columns,
        "base_temp": BASE_TEMP,
    }

    joblib.dump(
        model_data,
        MODEL_FILE,
    )

    print(f"Model saved to: {MODEL_FILE}")

if __name__ == "__main__":
    train_model()