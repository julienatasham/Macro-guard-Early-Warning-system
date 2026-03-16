import os
import pandas as pd
import logging

# -------------------------------
# Logging setup
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# -------------------------------
# Paths
# -------------------------------
BASE_DIR = os.path.dirname(__file__)
RAW_FOLDER = os.path.join(BASE_DIR, "../data/raw")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "../data/clean")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

FX_FILE = os.path.join(RAW_FOLDER, "fx.csv")
FUEL_FILE = os.path.join(RAW_FOLDER, "fuelprice.csv")
INFLATION_FILE = os.path.join(RAW_FOLDER, "inflation.csv")
INTEREST_FILE = os.path.join(RAW_FOLDER, "interest.csv")

CLEAN_CSV_FILE = os.path.join(OUTPUT_FOLDER, "merged_clean.csv")
CLEAN_PARQUET_FILE = os.path.join(OUTPUT_FOLDER, "merged_clean.parquet")

# -------------------------------
# Utility function to load CSV safely
# -------------------------------
def load_csv(file_path, parse_dates=None, columns=None):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, parse_dates=parse_dates)
            logger.info(f"Loaded {len(df)} rows from {file_path}")
            return df
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            if columns:
                return pd.DataFrame(columns=columns)
            return pd.DataFrame()
    else:
        logger.warning(f"{file_path} not found, creating empty DataFrame")
        return pd.DataFrame(columns=columns)

# -------------------------------
# Main cleaning function
# -------------------------------
def clean_daily_data():
    logger.info("Starting daily data cleaning pipeline")

    # 1️⃣ Load datasets safely
    fx_df = load_csv(FX_FILE, parse_dates=['Date'], columns=['Date', 'fx_kes_usd'])
    fuel_df = load_csv(FUEL_FILE, parse_dates=['Date'], columns=['Date', 'fuel_price_usd'])
    inflation_df = load_csv(INFLATION_FILE, columns=['year', 'inflation_rate'])
    interest_df = load_csv(INTEREST_FILE, columns=['year', 'interest_rate'])

    # 2️⃣ Forward-fill FX & Fuel
    if not fx_df.empty:
        fx_df = fx_df.dropna(subset=['Date'])
        fx_df['fx_kes_usd'] = fx_df['fx_kes_usd'].ffill()
    if not fuel_df.empty:
        fuel_df = fuel_df.dropna(subset=['Date'])
        fuel_df['fuel_price_usd'] = fuel_df['fuel_price_usd'].ffill()

    # 3️⃣ Prepare daily Inflation
    if not inflation_df.empty:
        inflation_df['Date'] = pd.to_datetime(inflation_df['year'].astype(str) + '-01-01')
        inflation_daily = (
            inflation_df[['Date', 'inflation_rate']]
            .set_index('Date')
            .resample('D')
            .ffill()
            .reset_index()
        )
    else:
        inflation_daily = pd.DataFrame(columns=['Date', 'inflation_rate'])

    # 4️⃣ Prepare daily Interest Rates
    if not interest_df.empty:
        interest_df['Date'] = pd.to_datetime(interest_df['year'].astype(str) + '-01-01')
        interest_daily = (
            interest_df[['Date', 'interest_rate']]
            .set_index('Date')
            .resample('D')
            .ffill()
            .reset_index()
        )
    else:
        interest_daily = pd.DataFrame(columns=['Date', 'interest_rate'])

    # 5️⃣ Merge datasets safely from any non-empty dataframe
    dfs_to_merge = []
    if not fx_df.empty:
        dfs_to_merge.append(fx_df)
    if not fuel_df.empty:
        dfs_to_merge.append(fuel_df)
    if not inflation_daily.empty:
        dfs_to_merge.append(inflation_daily)
    if not interest_daily.empty:
        dfs_to_merge.append(interest_daily)

    if dfs_to_merge:
        merged_df = dfs_to_merge[0].sort_values('Date')
        for df in dfs_to_merge[1:]:
            merged_df = pd.merge_asof(
                merged_df,
                df.sort_values('Date'),
                on='Date',
                direction='backward',
                tolerance=pd.Timedelta('365D')  # large tolerance for yearly data
            )
    else:
        merged_df = pd.DataFrame()

    # 6️⃣ Append only new rows to existing clean dataset
    if os.path.exists(CLEAN_CSV_FILE):
        old_df = pd.read_csv(CLEAN_CSV_FILE, parse_dates=['Date'])
        if not merged_df.empty:
            last_date = old_df['Date'].max()
            new_df = merged_df[merged_df['Date'] > last_date]
            if not new_df.empty:
                final_df = pd.concat([old_df, new_df])
                logger.info(f"Appending {len(new_df)} new rows to clean dataset")
            else:
                final_df = old_df
                logger.info("No new rows to append, dataset up to date")
        else:
            final_df = old_df
            logger.info("Merged dataset empty, keeping old dataset")
    else:
        final_df = merged_df
        logger.info("Creating new clean dataset")

    # 7️⃣ Save cleaned dataset
    if not final_df.empty:
        final_df.to_csv(CLEAN_CSV_FILE, index=False)
        final_df.to_parquet(CLEAN_PARQUET_FILE, index=False)
        logger.info(f"Cleaned dataset saved to {CLEAN_CSV_FILE} and {CLEAN_PARQUET_FILE}")
    else:
        logger.warning("Final merged dataset is empty, nothing to save")

    logger.info("Daily cleaning pipeline completed successfully")
    return final_df

# -------------------------------
# Run script
# -------------------------------
if __name__ == "__main__":
    df = clean_daily_data()
    logger.info(df.head() if not df.empty else "Merged dataset is empty")