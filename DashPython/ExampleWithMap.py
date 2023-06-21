import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

# Read the CSV file
df = pd.read_csv('https://raw.githubusercontent.com/catauggie/ChatGPT/main/2018.csv')

# Create the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.H1("Dashboard"),
    html.H2("Filters"),
    dcc.Dropdown(
        id='country-filter',
        options=[{'label': country, 'value': country} for country in df['Country or region'].unique()],
        value=[],
        multi=True
    ),
    html.H2("Choropleth Map"),
    dcc.Graph(
        id='choropleth-map'
    ),
    html.H2("Bar Chart"),
    dcc.Graph(
        id='bar-chart'
    ),
    html.H2("Top 10 Countries or Regions"),
    dash_table.DataTable(
        id='table',
        columns=[{"name": col, "id": col} for col in df.columns],
        data=df.to_dict('records')
    )
])


# Callback to update the choropleth map, bar chart, and table based on the selected country filter
@app.callback(
    Output('choropleth-map', 'figure'),
    Output('bar-chart', 'figure'),
    Output('table', 'data'),
    Input('country-filter', 'value')
)
def update_data(selected_countries):
    if selected_countries:
        filtered_df = df[df['Country or region'].isin(selected_countries)]

        # Update the choropleth map
        choropleth_map = px.choropleth(
            filtered_df,
            locations='Country or region',
            locationmode='country names',
            color='Score',
            title='Happiness Scores by Country'
        )

        # Update the bar chart
        bar_chart = px.bar(filtered_df, x='Score', y='Country or region', orientation='h', title='Scores by Country')

        # Update the table data
        table_data = filtered_df.to_dict('records')

        return choropleth_map, bar_chart, table_data
    else:
        choropleth_map = px.choropleth(
            df,
            locations='Country or region',
            locationmode='country names',
            color='Score',
            title='Happiness Scores by Country'
        )

        bar_chart = px.bar(df, x='Score', y='Country or region', orientation='h', title='Scores by Country')

        return choropleth_map, bar_chart, df.to_dict('records')


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
