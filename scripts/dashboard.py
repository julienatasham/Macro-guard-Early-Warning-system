import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Load CSV and clean column names
df = pd.read_csv(
    r"C:\Users\USER\OneDrive\Desktop\projects\Macro-guard Early Warning system\data\features\forecasted_features.csv"
)
df.columns = df.columns.str.strip()  # remove any hidden whitespace

# Ensure 'Date' is datetime
df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce')
df = df.dropna(subset=['Date'])  # drop rows where Date could not be parsed
df = df.sort_values('Date')

# Create % change features for trends
df_pct = df.copy()
df_pct['fuel_price_usd_pct'] = df_pct['fuel_price_usd'].pct_change() * 100
df_pct['inflation_rate_pct'] = df_pct['inflation_rate'].pct_change() * 100
df_pct['interest_rate_pct'] = df_pct['interest_rate'].pct_change() * 100

# Initialize Dash
app = dash.Dash(__name__)
app.title = "MacroGuard Early Warning Dashboard"

# Layout
app.layout = html.Div(style={'backgroundColor': '#1e003b', 'color': '#fff', 'font-family': 'Arial'}, children=[
    html.H1("MacroGuard Dashboard", style={'textAlign': 'center', 'color': '#ff66b2', 'padding': '20px'}),

    dcc.Tabs([
        dcc.Tab(label='Raw Features', style={'backgroundColor': '#330033', 'color': '#ff66b2'},
                selected_style={'backgroundColor': '#ff66b2', 'color': '#330033'}, children=[
            dcc.Graph(
                figure=px.line(df, x='Date', y=['fuel_price_usd', 'inflation_rate', 'interest_rate'],
                               title="Raw Feature Trends",
                               color_discrete_sequence=['#ff66b2', '#cc66ff', '#ff99cc'])
            )
        ]),

        dcc.Tab(label='Percentage Change', style={'backgroundColor': '#330033', 'color': '#ff66b2'},
                selected_style={'backgroundColor': '#ff66b2', 'color': '#330033'}, children=[
            dcc.Graph(
                figure=px.line(df_pct, x='Date',
                               y=['fuel_price_usd_pct', 'inflation_rate_pct', 'interest_rate_pct'],
                               title="% Change Over Time",
                               color_discrete_sequence=['#ff66b2', '#cc66ff', '#ff99cc'])
            )
        ]),

        dcc.Tab(label='Forecast Summary', style={'backgroundColor': '#330033', 'color': '#ff66b2'},
                selected_style={'backgroundColor': '#ff66b2', 'color': '#330033'}, children=[
            dcc.Graph(
                figure=go.Figure(data=[
                    go.Scatter(x=df['Date'], y=df['fuel_price_usd'], mode='lines+markers', name='Fuel Price USD',
                               line=dict(color='#ff66b2', width=3)),
                    go.Scatter(x=df['Date'], y=df['inflation_rate'], mode='lines+markers', name='Inflation Rate',
                               line=dict(color='#cc66ff', width=3)),
                    go.Scatter(x=df['Date'], y=df['interest_rate'], mode='lines+markers', name='Interest Rate',
                               line=dict(color='#ff99cc', width=3))
                ], layout=go.Layout(
                    title="Forecasted Features Overview",
                    plot_bgcolor='#330033',
                    paper_bgcolor='#1e003b',
                    font=dict(color='#ff66b2'),
                    xaxis=dict(title='Date'),
                    yaxis=dict(title='Values')
                ))
            )
        ]),

        dcc.Tab(label='Data Table', style={'backgroundColor': '#330033', 'color': '#ff66b2'},
                selected_style={'backgroundColor': '#ff66b2', 'color': '#330033'}, children=[
            dash.dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_header={'backgroundColor': '#330033', 'color': '#ff66b2', 'fontWeight': 'bold'},
                style_cell={'backgroundColor': '#1e003b', 'color': '#fff', 'textAlign': 'center'}
            )
        ])
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)