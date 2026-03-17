# scripts/forecasting.py
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# 1️⃣ Paths
base_dir = os.path.dirname(os.path.dirname(__file__))
features_dir = os.path.join(base_dir, 'data', 'features')
features_file = os.path.join(features_dir, 'features_dataset.csv')
forecast_file = os.path.join(features_dir, 'forecasted_features.csv')

# 2️⃣ Load features dataset
df = pd.read_csv(features_file)

# Ensure 'Date' column exists and is datetime
if 'Date' not in df.columns:
    raise ValueError("The features dataset must have a 'Date' column.")
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])
df = df.sort_values('Date')
df.set_index('Date', inplace=True)

# 3️⃣ Columns to forecast
target_cols = ['fuel_price_usd', 'inflation_rate', 'interest_rate']

# Ensure target columns exist
for col in target_cols:
    if col not in df.columns:
        raise ValueError(f"Missing required column: {col}")

# 4️⃣ Prepare features (X) and target (y)
predictor_cols = [c for c in df.columns if c not in target_cols]
X = df[predictor_cols]
y = df[target_cols]

# Fill any missing values
X = X.fillna(method='ffill')
y = y.fillna(method='ffill')

# Standardize predictors
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train-test split: last row for real-time forecast
X_train = X_scaled[:-1]
y_train = y[:-1]
X_next = X_scaled[-1].reshape(1, -1)

# 5️⃣ Train a RandomForest for each target and predict next month
preds = {}
for col in target_cols:
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train[col])
    preds[col] = model.predict(X_next)[0]

# 6️⃣ Forecast next date (assuming monthly data)
last_date = df.index[-1]
next_date = last_date + pd.DateOffset(months=1)

# 7️⃣ Create forecast DataFrame
forecast_row = pd.DataFrame(preds, index=[next_date])

# 8️⃣ Save / append to forecast CSV safely
os.makedirs(features_dir, exist_ok=True)
if os.path.exists(forecast_file):
    df_forecast = pd.read_csv(forecast_file)
    df_forecast['Date'] = pd.to_datetime(df_forecast['Date'], errors='coerce')
    df_forecast = df_forecast.dropna(subset=['Date'])
    df_forecast.set_index('Date', inplace=True)
    
    # Remove duplicate date if exists
    df_forecast = df_forecast[~df_forecast.index.duplicated(keep='last')]
    
    # Append new forecast
    df_forecast = pd.concat([df_forecast, forecast_row])
else:
    df_forecast = forecast_row

df_forecast.to_csv(forecast_file)
print(f"✅ Forecasted features saved to {forecast_file}")
print(forecast_row)