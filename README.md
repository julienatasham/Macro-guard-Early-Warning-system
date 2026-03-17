# INTRODUCTION

-MacroGuard is a real-time economic stress monitoring platform designed to detect early signals of macroeconomic instability. The system automatically collects live economic indicators such as exchange rates, inflation data, and interest rates from external APIs, processes and stores the data through a structured pipeline, and generates risk signals using statistical and machine learning models. By continuously updating and analyzing these indicators, MacroGuard provides a dynamic view of economic conditions and flags potential stress events before they escalate into crises.

## project structure

macroguard
│
├── config
│   settings.py
│
├── ingestion
│   fx_api.py
│   inflation_api.py
│   interest_rates_api.py
│
├── pipelines
│   data_pipeline.py
│   forecast_model.py
│
├── storage
│   database.py
│
├── api
│   app.py
│
├── data
│   raw
│   clean
│
└── main.py

## Real-Time Feature Pipeline

This script will:

Read the daily cleaned dataset (merged_clean.csv)

Calculate rolling indicators like:

7-day, 30-day FX volatility

Monthly fuel price changes

Yearly inflation delta

Interest rate trends

Normalize features for modeling or dashboard consumption

Generate a composite “economic stress score”

Save to CSV/Parquet for your dashboard or forecasting module

## Real-Time Design Notes

Use incremental updates: only compute new rows, append to existing feature table.

Keep all computations vectorized with Pandas to avoid heavy SSD writes.

Optional: Use SQLite or DuckDB for more scalable real-time storage.

Later, when connecting to the cloud, you can read directly from AWS S3 / GCP bucket and write processed features without touching local SSD much.
