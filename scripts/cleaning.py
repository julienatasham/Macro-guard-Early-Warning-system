# scripts/cleaning_daily.py
import pandas as pd
import os

# -------------------------------
# 1️⃣ Paths to raw and clean data
# -------------------------------
raw_folder = os.path.join(os.path.dirname(__file__), "../data/raw")
output_folder = os.path.join(os.path.dirname(__file__), "../data/clean")
os.makedirs(output_folder, exist_ok=True)

fx_file = os.path.join(raw_folder, "fx.csv")
fuel_file = os.path.join(raw_folder, "fuelprice.csv")
inflation_file = os.path.join(raw_folder, "inflation.csv")
interest_file = os.path.join(raw_folder, "interest.csv")

# -------------------------------
# 2️⃣ Load datasets and drop null dates
# -------------------------------
fx_df = pd.read_csv(fx_file, parse_dates=['Date']).dropna(subset=['Date'])
fuel_df = pd.read_csv(fuel_file, parse_dates=['Date']).dropna(subset=['Date'])
inflation_df = pd.read_csv(inflation_file)
interest_df = pd.read_csv(interest_file)

# -------------------------------
# 3️⃣ Forward-fill FX & Fuel prices
# -------------------------------
fx_df['fx_kes_usd'] = fx_df['fx_kes_usd'].ffill()
fuel_df['fuel_price_usd'] = fuel_df['fuel_price_usd'].ffill()

# -------------------------------
# 4️⃣ Prepare Inflation
# -------------------------------
# Map yearly inflation to Jan 1 of each year
inflation_df['Date'] = pd.to_datetime(inflation_df['year'].astype(str) + '-01-01')
inflation_df = inflation_df[['Date', 'inflation_rate']]

# Resample daily and forward-fill
inflation_daily = inflation_df.set_index('Date').resample('D').ffill().reset_index()

# -------------------------------
# 5️⃣ Prepare Interest Rates
# -------------------------------
interest_df['Date'] = pd.to_datetime(interest_df['year'].astype(str) + '-01-01')
interest_df = interest_df[['Date', 'interest_rate']]

# Resample daily and forward-fill
interest_daily = interest_df.set_index('Date').resample('D').ffill().reset_index()

# -------------------------------
# 6️⃣ Merge datasets daily
# -------------------------------
# Start from FX, which is usually daily
merged_df = pd.merge_asof(fx_df.sort_values('Date'), 
                          fuel_df.sort_values('Date'), on='Date')

merged_df = pd.merge_asof(merged_df.sort_values('Date'),
                          inflation_daily.sort_values('Date'), on='Date')

merged_df = pd.merge_asof(merged_df.sort_values('Date'),
                          interest_daily.sort_values('Date'), on='Date')

# -------------------------------
# 7️⃣ Save cleaned daily dataset
# -------------------------------
clean_file = os.path.join(output_folder, "merged_clean.csv")
merged_df.to_csv(clean_file, index=False)

print(f"Daily cleaned dataset saved to {clean_file}")
print(merged_df.head())