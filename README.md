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
│
├── processing
│   wrangling.py
│   feature_engineering.py
│
├── models
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
│   processed
│
└── main.py
