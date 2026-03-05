# scripts/ingestion.py
import os
import numpy as np
import pandas as pd
import yfinance as yf
import requests
import zipfile

# -------------------------------
# 1️⃣ Set up raw data folder
# -------------------------------
raw_folder = os.path.join(os.path.dirname(__file__), "../data/raw")
os.makedirs(raw_folder, exist_ok=True)

# -------------------------------
# 2️⃣ Download FX rates (USD/KES)
# -------------------------------
fx_file = os.path.join(raw_folder, "fx.csv")
print("Downloading FX rates (USD/KES)...")
fx_df = yf.download("USDKES=X", start="2000-01-01", end="2025-12-31")
fx_df = fx_df.reset_index()[['Date', 'Close']]
fx_df.rename(columns={'Close': 'fx_kes_usd'}, inplace=True)
fx_df.to_csv(fx_file, index=False)
print(f"FX data saved to {fx_file}\n")

# -------------------------------
# 3️⃣ Download Fuel Prices (Brent crude)
# -------------------------------
fuel_file = os.path.join(raw_folder, "fuelprice.csv")
print("Downloading fuel prices (Brent crude)...")
fuel_df = yf.download("BZ=F", start="2000-01-01", interval="1mo")
fuel_df = fuel_df.reset_index()[["Date", "Close"]]
fuel_df.rename(columns={"Close": "fuel_price_usd"}, inplace=True)
fuel_df.to_csv(fuel_file, index=False)
print(f"Fuel price data saved to {fuel_file}\n")

# -------------------------------
# 4️⃣ Download Inflation (World Bank)
# -------------------------------
inflation_file = os.path.join(raw_folder, "inflation.csv")
print("Downloading inflation data (World Bank)...")
wb_url = "http://api.worldbank.org/v2/en/indicator/FP.CPI.TOTL.ZG?downloadformat=csv"
response = requests.get(wb_url)

# Save temp ZIP
temp_zip = os.path.join(raw_folder, "inflation_temp.zip")
with open(temp_zip, "wb") as f:
    f.write(response.content)

# Extract CSV from ZIP
with zipfile.ZipFile(temp_zip) as z:
    csv_filename = [f for f in z.namelist() if f.endswith('.csv') and 'Metadata' not in f][0]
    with z.open(csv_filename) as f:
        df = pd.read_csv(f, skiprows=4)

kenya_df = df[df['Country Name'] == 'Kenya']
year_cols = [c for c in kenya_df.columns if c.isdigit()]
kenya_df = kenya_df.melt(
    id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'],
    value_vars=year_cols,
    var_name='year',
    value_name='inflation_rate'
)
kenya_df = kenya_df[['year', 'inflation_rate']].sort_values('year')
kenya_df['year'] = kenya_df['year'].astype(int)
kenya_df.to_csv(inflation_file, index=False)
print(f"Inflation data saved to {inflation_file}\n")

# -------------------------------
# 5️⃣ Interest Rates 
# -------------------------------
interest_file = os.path.join(raw_folder, "interest.csv")
print("Generating synthetic interest rates for Kenya...")

# Define time range
years = pd.date_range(start='2000-01-01', end='2025-12-31', freq='YS')  # yearly start
np.random.seed(42)

# Approximate realistic interest rates for Kenya
# e.g., historically ranged ~4% to ~15%
rates = np.random.uniform(4, 15, len(years))

interest_df = pd.DataFrame({
    'year': years.year,
    'interest_rate': rates
})
interest_df.to_csv(interest_file, index=False)
print(f"Synthetic interest rates saved to {interest_file}\n")
print("All datasets downloaded and saved successfully!")