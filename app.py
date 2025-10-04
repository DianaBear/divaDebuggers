import dash
from dash import dcc, html, Input, Output
import dash_leaflet as dl
import pandas as pd
import plotly.express as px

# load the CSV dataset
df = pd.read_csv("dataset.csv")

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "PestAlert SC"

# get unique regions
regions = df['region'].unique()

# function to determine marker color
def ndvi_color(ndvi):
    if ndvi > 0.7:
        return "purple"
    elif ndvi > 0.5:
        return "orange"
    else:
        return "yellow"

# create markers for map
markers = [
    dl.CircleMarker(
        center=(row["latitude"], row["longitude"]),
        radius=10,
        color=ndvi_color(row["ndvi"]),
        fillOpacity=0.6,
        children=[
            dl.Popup(f"{row['region']}<br>NDVI: {row['ndvi']}<br>Date: {row['date']}")
        ],
        id={"type": "marker", "index": idx}
    )
    for idx, row in df.iterrows()
]

# layout
app.layout = html.Div([
    html.H1("FlorAlert SC - Bloom Hotspots in South Carolina"),
    dl.Map(
        children=[
            dl.TileLayer(),
            dl.LayerGroup(markers)
        ],
        center=(33.9, -81),
        zoom=7,
        style={'width': '100%', 'height': '500px'}
    ),
    html.Br(),
    html.Label("Select a region:"),
    dcc.Dropdown(
        id='region-dropdown',
        options=[{"label": r, "value": r} for r in regions],
        value=regions[0]
    ),
    dcc.Graph(id='ndvi-chart')
])

# callback to update chart based on selected region
@app.callback(
    Output('ndvi-chart', 'figure'),
    Input('region-dropdown', 'value')
)
def update_chart(region):
    filtered = df[df['region'] == region]
    filtered['date'] = pd.to_datetime(filtered['date'])
    
    fig = px.line(
        filtered,
        x='date',
        y='ndvi',
        title=f"NDVI Trends for {region}",
        markers=True
    )

    # highlight bloom points
    fig.add_scatter(
        x=filtered[filtered['ndvi'] > 0.5]['date'],
        y=filtered[filtered['ndvi'] > 0.5]['ndvi'],
        mode='markers',
        marker=dict(color='orange', size=10),
        name='Potential Bloom'
    )

    fig.update_layout(
        yaxis=dict(range=[0,1], title='NDVI'),
        xaxis=dict(title='Date')
    )

    return fig

# run the app
if __name__ == '__main__':
    app.run_server(debug=True)
