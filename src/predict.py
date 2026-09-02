from pathlib import Path
import argparse
import joblib
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_FILE = PROJECT_ROOT / "models" / "ontario_demand_model.joblib"

def load_model():
    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            "Model not found. Run 'python src/train_model.py' first."
        )

    return joblib.load(MODEL_FILE)

def create_features(
    timestamp,
    toronto_temp,
    ottawa_temp,
    windsor_temp,
    sudbury_temp,
    thunder_bay_temp,
    feature_columns,
    base_temp,
):
    timestamp = pd.Timestamp(timestamp)
    hour = timestamp.hour
    hour_sin = np.sin(2 * np.pi * hour / 24)
    hour_cos = np.cos(2 * np.pi * hour / 24)

    temperatures = {
        "toronto_temp": toronto_temp,
        "ottawa_temp": ottawa_temp,
        "windsor_temp": windsor_temp,
        "sudbury_temp": sudbury_temp,
        "thunder_bay_temp": thunder_bay_temp,
    }

    avg_temp = np.mean(
        list(temperatures.values())
    )

    heating = max(
        base_temp - avg_temp,
        0,
    )

    cooling = max(
        avg_temp - base_temp,
        0,
    )

    features = {
        feature: 0
        for feature in feature_columns
    }

    features["hour_sin"] = hour_sin
    features["hour_cos"] = hour_cos

    for feature, value in temperatures.items():
        features[feature] = value

    features["heating"] = heating
    features["cooling"] = cooling

    day_feature = f"day_{timestamp.day_name()}"

    if day_feature in features:
        features[day_feature] = 1

    return pd.DataFrame(
        [[features[column] for column in feature_columns]],
        columns=feature_columns,
    )

def predict_demand(args):
    model_data = load_model()
    model = model_data["model"]
    feature_columns = model_data["features"]
    base_temp = model_data["base_temp"]

    X = create_features(
        timestamp=args.timestamp,
        toronto_temp=args.toronto_temp,
        ottawa_temp=args.ottawa_temp,
        windsor_temp=args.windsor_temp,
        sudbury_temp=args.sudbury_temp,
        thunder_bay_temp=args.thunder_bay_temp,
        feature_columns=feature_columns,
        base_temp=base_temp,
    )

    prediction = model.predict(X)[0]
    print(f"Timestamp: {args.timestamp}")
    print(
        f"Predicted Ontario demand: "
        f"{prediction:,.0f} MW"
    )

def main():
    parser = argparse.ArgumentParser(
        description="Predict hourly Ontario electricity demand."
    )

    parser.add_argument(
        "--timestamp",
        required=True,
        help='Timestamp such as "2025-12-15 18:00"',
    )

    parser.add_argument(
        "--toronto-temp",
        type=float,
        required=True,
    )

    parser.add_argument(
        "--ottawa-temp",
        type=float,
        required=True,
    )

    parser.add_argument(
        "--windsor-temp",
        type=float,
        required=True,
    )

    parser.add_argument(
        "--sudbury-temp",
        type=float,
        required=True,
    )

    parser.add_argument(
        "--thunder-bay-temp",
        type=float,
        required=True,
    )

    args = parser.parse_args()
    predict_demand(args)

if __name__ == "__main__":
    main()