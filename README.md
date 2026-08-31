# Ontario Electricity Demand Predictor

A machine learning project that predicts hourly electricity demand in Ontario using time and weather data.

The project uses real electricity demand data from IESO and historical weather data from Environment and Climate Change Canada.

## Goal

Predict Ontario's hourly electricity demand using:

- time of day
- day of week
- temperature from multiple Ontario cities

The model used is linear regression.

## Data Sources

### Electricity Demand

Hourly Ontario demand data comes from IESO.

The prediction target is:

```text
ontario_demand
```

### Weather

Hourly temperature data comes from Environment and Climate Change Canada.

Weather stations are used for:

- Toronto
- Ottawa
- Windsor
- Sudbury
- Thunder Bay

The downloader automatically chooses the station with the best data coverage for the requested year.

## Model Results

Several versions of the model were tested.

| Model | RMSE |
|---|---:|
| Hour only | 1724.23 MW |
| Cyclical hour | 1566.64 MW |
| Cyclical hour + weekday | 1558.77 MW |
| Multi-city weather | 1420.13 MW |
| Quadratic temperature | 1468.92 MW |
| Heating/cooling features | **1076.48 MW** |

The final model reduced RMSE by about **38%** compared with the original baseline.

## Final Features

The final model uses:

```text
hour_sin
hour_cos

day of week features

toronto_temp
ottawa_temp
windsor_temp
sudbury_temp
thunder_bay_temp

heating
cooling
```

Hour is represented using sine and cosine because time is cyclical.

Heating and cooling features are created using an average Ontario temperature:

```text
heating = max(18 - average_temperature, 0)

cooling = max(average_temperature - 18, 0)
```

This helped the model represent the higher electricity demand that can happen during very cold or very hot weather.

## Technologies

- Python
- pandas
- NumPy
- scikit-learn
- PostgreSQL
- SQLAlchemy
- Docker
- Jupyter Notebook