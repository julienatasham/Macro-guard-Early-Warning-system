# scripts/features.py
import os
import pandas as pd
import numpy as np

# 1️⃣ Paths
base_dir = os.path.dirname(os.path.dirname(__file__))
clean_dir = os.path.join(base_dir, 'data', 'clean')
input_file = os.path.join(clean_dir, 'merged_clean.csv')
output_file = os.path.join(clean_dir, 'features_dataset.csv')

# 2️⃣ Load cleaned dataset
df = pd.read_csv(input_file, parse_dates=['Date'])
df = df.sort_values('Date')
df.set_index('Date', inplace=True)

# 3️⃣ Compute daily percent changes
df['interest_pct_change'] = df['interest_rate'].pct_change() * 100
df['fuel_pct_change'] = df['fuel_price_usd'].pct_change() * 100
df['inflation_pct_change'] = df['inflation_rate'].pct_change() * 100

# 4️⃣ Compute rolling averages (7-day and 30-day)
rolling_windows = [7, 30]
for window in rolling_windows:
    df[f'interest_roll_{window}'] = df['interest_rate'].rolling(window).mean()
    df[f'fuel_roll_{window}'] = df['fuel_price_usd'].rolling(window).mean()
    df[f'inflation_roll_{window}'] = df['inflation_rate'].rolling(window).mean()

# 5️⃣ Compute z-scores
for col in ['interest_rate', 'fuel_price_usd', 'inflation_rate']:
    df[f'{col}_zscore'] = (df[col] - df[col].mean()) / df[col].std()

# 6️⃣ Forward-fill nulls
df.ffill(inplace=True)

# 7️⃣ Save
os.makedirs(clean_dir, exist_ok=True)
df.to_csv(output_file)
print(f"✅ Feature dataset saved to {output_file}")
print(df.head())