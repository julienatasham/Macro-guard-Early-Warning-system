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
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
df = df.sort_index()

# 3️⃣ Columns to forecast
target_cols = ['fuel_price_usd', 'inflation_rate', 'interest_rate']

# 4️⃣ Prepare predictors
predictor_cols = [c for c in df.columns if c not in target_cols]

# ✅ Forward-fill missing values here, before scaling
X = df[predictor_cols].ffill()
y = df[target_cols].ffill()

# 5️⃣ Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # this is now safe

# 6️⃣ Train-test split (last row is for real-time forecast)
X_train = X_scaled[:-1]
y_train = y[:-1]
X_next = X_scaled[-1].reshape(1, -1)

# 7️⃣ Train a RandomForest for each target column
preds = {}
for col in target_cols:
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train[col])
    preds[col] = model.predict(X_next)[0]

# 8️⃣ Create forecasted row
next_date = df.index[-1] + pd.DateOffset(months=1)
forecast_row = pd.DataFrame(preds, index=[next_date])

# 9️⃣ Save or append to forecast CSV
os.makedirs(features_dir, exist_ok=True)
if os.path.exists(forecast_file):
    forecast_df = pd.read_csv(forecast_file)
    if 'Date' in forecast_df.columns:
        forecast_df['Date'] = pd.to_datetime(forecast_df['Date'])
        forecast_df.set_index('Date', inplace=True)
    forecast_df = pd.concat([forecast_df, forecast_row])
else:
    forecast_df = forecast_row

forecast_df.to_csv(forecast_file)
print(f"✅ Forecasted features saved to {forecast_file}")
print(forecast_row)