import os
import pandas as pd
import yfinance as yf
import requests
import zipfile
import logging
from datetime import datetime

# -------------------------------------------------
# Logging setup
# -------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -------------------------------------------------
# Raw data folder
# -------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
RAW_FOLDER = os.path.join(BASE_DIR, "../data/raw")

os.makedirs(RAW_FOLDER, exist_ok=True)

# -------------------------------------------------
# Utility function
# -------------------------------------------------
def load_existing(file_path):

    if os.path.exists(file_path):
        return pd.read_csv(file_path)

    return pd.DataFrame()


# -------------------------------------------------
# FX DATA (USD/KES)
# -------------------------------------------------
def update_fx():

    logging.info("Updating FX data")

    file_path = os.path.join(RAW_FOLDER, "fx.csv")

    existing = load_existing(file_path)

    if not existing.empty:
        last_date = existing["Date"].max()
    else:
        last_date = "2000-01-01"

    today = datetime.today().strftime("%Y-%m-%d")

    try:

        fx_new = yf.download(
            "USDKES=X",
            start=last_date,
            end=today,
            progress=False
        )

        if fx_new.empty:
            logging.warning("No new FX data found")
            return

        fx_new = fx_new.reset_index()[["Date", "Close"]]
        fx_new.rename(columns={"Close": "fx_kes_usd"}, inplace=True)

        combined = pd.concat([existing, fx_new])
        combined = combined.drop_duplicates(subset="Date")

        combined.to_csv(file_path, index=False)

        logging.info("FX data updated")

    except Exception as e:
        logging.error(f"FX ingestion failed: {e}")


# -------------------------------------------------
# FUEL PRICES (Brent crude)
# -------------------------------------------------
def update_fuel():

    logging.info("Updating fuel prices")

    file_path = os.path.join(RAW_FOLDER, "fuelprice.csv")

    try:

        fuel = yf.download(
            "BZ=F",
            start="2000-01-01",
            interval="1mo",
            progress=False
        )

        fuel = fuel.reset_index()[["Date", "Close"]]
        fuel.rename(columns={"Close": "fuel_price_usd"}, inplace=True)

        fuel.to_csv(file_path, index=False)

        logging.info("Fuel data updated")

    except Exception as e:
        logging.error(f"Fuel ingestion failed: {e}")


# -------------------------------------------------
# INFLATION (World Bank)
# -------------------------------------------------
def update_inflation():

    logging.info("Downloading inflation data")

    file_path = os.path.join(RAW_FOLDER, "inflation.csv")

    try:

        url = "http://api.worldbank.org/v2/en/indicator/FP.CPI.TOTL.ZG?downloadformat=csv"

        response = requests.get(url)

        temp_zip = os.path.join(RAW_FOLDER, "inflation_temp.zip")

        with open(temp_zip, "wb") as f:
            f.write(response.content)

        with zipfile.ZipFile(temp_zip) as z:

            csv_file = [
                f for f in z.namelist()
                if f.endswith(".csv") and "Metadata" not in f
            ][0]

            with z.open(csv_file) as f:
                df = pd.read_csv(f, skiprows=4)

        kenya = df[df["Country Name"] == "Kenya"]

        year_cols = [c for c in kenya.columns if c.isdigit()]

        kenya = kenya.melt(
            id_vars=[
                "Country Name",
                "Country Code",
                "Indicator Name",
                "Indicator Code"
            ],
            value_vars=year_cols,
            var_name="year",
            value_name="inflation_rate"
        )

        kenya = kenya[["year", "inflation_rate"]]

        kenya["year"] = kenya["year"].astype(int)

        kenya = kenya.sort_values("year")

        kenya.to_csv(file_path, index=False)

        logging.info("Inflation data updated")

    except Exception as e:
        logging.error(f"Inflation ingestion failed: {e}")


# -------------------------------------------------
# INTEREST RATES (temporary synthetic data)
# -------------------------------------------------
def update_interest():

    logging.info("Generating synthetic interest rates")

    file_path = os.path.join(RAW_FOLDER, "interest.csv")

    try:

        years = pd.date_range(
            start="2000-01-01",
            end="2025-12-31",
            freq="YS"
        )

        import numpy as np
        np.random.seed(42)

        rates = np.random.uniform(4, 15, len(years))

        df = pd.DataFrame({
            "year": years.year,
            "interest_rate": rates
        })

        df.to_csv(file_path, index=False)

        logging.info("Interest rates saved")

    except Exception as e:
        logging.error(f"Interest ingestion failed: {e}")


# -------------------------------------------------
# MAIN PIPELINE
# -------------------------------------------------
def run_pipeline():

    logging.info("Starting data ingestion pipeline")

    update_fx()
    update_fuel()
    update_inflation()
    update_interest()

    logging.info("All datasets updated successfully")


# -------------------------------------------------
# RUN SCRIPT
# -------------------------------------------------
if __name__ == "__main__":

    run_pipeline()