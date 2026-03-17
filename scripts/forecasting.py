# forecasting.py (updated)
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
# ... your other imports

# -------------------------
# After you generate your forecast DataFrame
# Suppose it's called df_forecast
# -------------------------

# Ensure the date column exists
if 'Date' in df_forecast.columns:
    df_forecast.rename(columns={'Date': 'date'}, inplace=True)

# If any dates are missing or incorrect, fill with today's date or increment
# Convert to datetime safely
df_forecast['date'] = pd.to_datetime(df_forecast['date'], errors='coerce')

# Replace any invalid dates (NaT) with sequential dates starting from last valid date
if df_forecast['date'].isna().any():
    # Find last valid date
    last_valid = df_forecast['date'].max()
    if pd.isna(last_valid):
        last_valid = pd.Timestamp.today()
    # Fill NaT with incremental daily dates
    na_indices = df_forecast['date'].isna()
    df_forecast.loc[na_indices, 'date'] = [
        last_valid + pd.Timedelta(days=i+1)
        for i in range(na_indices.sum())
    ]

# Sort by date
df_forecast = df_forecast.sort_values('date').reset_index(drop=True)

# Save CSV
forecast_file = 'data/features/forecasted_features.csv'
df_forecast.to_csv(forecast_file, index=False)
print(f"✅ Forecasted features saved to {forecast_file}")