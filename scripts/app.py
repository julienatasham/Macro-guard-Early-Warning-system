import pandas as pd
import streamlit as st
import plotly.express as px

# -------------------------
# Load Data
# -------------------------
df = pd.read_csv("data/features/forecasted_features.csv")

# Clean column names
df.columns = df.columns.str.strip().str.replace('\ufeff', '')

# Create step index instead of Date
df['Step'] = range(1, len(df) + 1)

# -------------------------
# Page Config
# -------------------------
st.set_page_config(
    page_title="MacroGuard",
    layout="wide",
    page_icon="📊"
)

# -------------------------
# Styling (Pink + Purple)
# -------------------------
st.markdown("""
<style>
body {
    background-color: #1a0033;
    color: white;
}
h1, h2, h3 {
    color: #ff66b2;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Sidebar
# -------------------------
st.sidebar.title("💜 MacroGuard")
tab = st.sidebar.radio(
    "Navigate",
    ["Overview", "Trends", "Data", "KPIs"]
)

# -------------------------
# Overview
# -------------------------
if tab == "Overview":
    st.title("📊 MacroGuard Early Warning System")
    st.write("Welcome to MacroGuard - your macro-economic forecasting dashboard")

# -------------------------
# Trends
# -------------------------
elif tab == "Trends":
    st.title("📈 Economic Trends")
    st.write("Visualize economic trends over time")

# -------------------------
# Data Table
# -------------------------
elif tab == "Data":
    st.title("📄 Forecast Data")
    st.dataframe(df, use_container_width=True)

# -------------------------
# KPIs
# -------------------------
elif tab == "KPIs":
    st.title("✨ Key Indicators")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Fuel Price",
        f"{df['fuel_price_usd'].iloc[-1]:.2f}",
        f"{df['fuel_price_usd'].pct_change().iloc[-1]*100:.2f}%"
    )

    col2.metric(
        "Inflation",
        f"{df['inflation_rate'].iloc[-1]:.2f}%",
        f"{df['inflation_rate'].pct_change().iloc[-1]*100:.2f}%"
    )

    col3.metric(
        "Interest Rate",
        f"{df['interest_rate'].iloc[-1]:.2f}%",
        f"{df['interest_rate'].pct_change().iloc[-1]*100:.2f}%"
    )