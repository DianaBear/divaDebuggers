
# # app.py
# import dash
# from dash import dcc, html, Input, Output
# import dash_leaflet as dl
# import pandas as pd
# import numpy as np
# import plotly.express as px

# # ---------- FAKE DATA ----------
# dates = pd.date_range(start="2025-01-01", end="2025-12-31", freq="7D")
# num_points = len(dates)

# flowers = ["Sunflower", "Daisy", "Rose", "Lily", "Tulip"]
# pests = {
#     "Sunflower": ["Beetle", "Aphid"],
#     "Daisy": ["Caterpillar", "Moth"],
#     "Rose": ["Thrips", "Aphid"],
#     "Lily": ["Moth", "Beetle"],
#     "Tulip": ["Thrips", "Caterpillar"]
# }

# # Generate dataset
# data = {
#     "date": dates,
#     "flower": np.random.choice(flowers, size=num_points),
#     "ndvi": np.random.uniform(0.3, 0.8, size=num_points),
#     "lat": np.random.uniform(32, 35, size=num_points),
#     "lon": np.random.uniform(-83, -78, size=num_points)
# }

# df = pd.DataFrame(data)
# df["bloom"] = df["ndvi"] > 0.5  # NDVI threshold for bloom

# # Add pest info based on flower
# def assign_pest(row):
#     flower = row["flower"]
#     if row["bloom"]:
#         return np.random.choice(pests[flower])
#     else:
#         return "No pests"

# df["common_pest"] = df.apply(assign_pest, axis=1)

# # ---------- DASH APP ----------
# app = dash.Dash(__name__)
# app.title = "Bloom & Pest Tracker SC"

# app.layout = html.Div([
#     html.H1("Bloom & Pest Tracker SC", style={"textAlign": "center", "color": "white"}),

#     html.Div([
#         html.Label("Select Flower:", style={"color": "white"}),
#         dcc.Dropdown(
#             id="flower-dropdown",
#             options=[{"label": f, "value": f} for f in flowers],
#             value="Sunflower",
#             style={"width": "300px"}
#         )
#     ], style={"width": "300px", "margin": "auto"}),

#     html.Div(dl.Map(center=[33.5, -80.5], zoom=7, id="bloom-map", style={"width": "100%", "height": "500px"})),
#     html.Div(dcc.Graph(id="bloom-graph"))
# ], style={"backgroundColor": "#0B3D91", "padding": "20px"})

# # ---------- CALLBACK ----------
# @app.callback(
#     Output("bloom-map", "children"),
#     Output("bloom-graph", "figure"),
#     Input("flower-dropdown", "value")
# )
# def update_flower(flower_name):
#     df_filtered = df[df["flower"] == flower_name]

#     # --- Map markers ---
#     markers = [
#         dl.Marker(
#             position=[row["lat"], row["lon"]],
#             children=dl.Popup(html.Div([
#                 html.B(f"{row['flower']}"),
#                 html.Br(),
#                 f"Bloom: {'Yes' if row['bloom'] else 'No'}",
#                 html.Br(),
#                 f"Pest: {row['common_pest']}"
#             ]))
#         )
#         for i, row in df_filtered.iterrows()
#     ]

#     tile_layer = dl.TileLayer(url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")

#     # --- Graph ---
#     fig = px.line(df_filtered, x="date", y="ndvi", title=f"{flower_name} NDVI & Bloom Periods",
#                   labels={"ndvi": "NDVI"})
#     fig.add_scatter(x=df_filtered[df_filtered["bloom"]]["date"],
#                     y=df_filtered[df_filtered["bloom"]]["ndvi"],
#                     mode="markers",
#                     marker=dict(color="orange", size=10),
#                     name="Bloom")
#     fig.update_layout(plot_bgcolor="#0B3D91", paper_bgcolor="#0B3D91", font_color="white")

#     return [tile_layer] + markers, fig

# # ---------- RUN APP ----------
# if __name__ == "__main__":
#     app.run(debug=True)



import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_leaflet as dl
import pandas as pd
import plotly.express as px

# Flowers and example data (update dates/pests as needed)
data = [
    {"flower": "Aster", "lat": 34.5, "lon": -81.2, "bloom_start":"2025-09-01","bloom_end":"2025-10-15",
     "pest_name":"Aphids", "pest_start":"2025-09-10","pest_end":"2025-10-20"},
    {"flower": "Columbine", "lat": 34.0, "lon": -81.5, "bloom_start":"2025-04-15","bloom_end":"2025-05-30",
     "pest_name":"Leaf Miners", "pest_start":"2025-04-20","pest_end":"2025-06-05"},
    {"flower": "Daffodil", "lat": 34.2, "lon": -81.3, "bloom_start":"2025-03-01","bloom_end":"2025-04-15",
     "pest_name":"Bulb Mites", "pest_start":"2025-03-05","pest_end":"2025-04-20"},
    {"flower": "Joe Pye Weed", "lat": 34.7, "lon": -81.0, "bloom_start":"2025-07-01","bloom_end":"2025-09-01",
     "pest_name":"Japanese Beetle", "pest_start":"2025-07-05","pest_end":"2025-09-05"},
    {"flower": "Milkweed", "lat": 33.9, "lon": -81.1, "bloom_start":"2025-06-01","bloom_end":"2025-08-15",
     "pest_name":"Milkweed Bugs", "pest_start":"2025-06-05","pest_end":"2025-08-20"},
    {"flower": "Bee Balm", "lat": 34.3, "lon": -81.4, "bloom_start":"2025-05-15","bloom_end":"2025-07-30",
     "pest_name":"Powdery Mildew", "pest_start":"2025-05-20","pest_end":"2025-08-05"},
    {"flower": "Goldenrod", "lat": 34.1, "lon": -81.2, "bloom_start":"2025-08-01","bloom_end":"2025-10-01",
     "pest_name":"Leafhoppers", "pest_start":"2025-08-05","pest_end":"2025-10-05"},
    {"flower": "Daisy", "lat": 34.6, "lon": -81.0, "bloom_start":"2025-04-01","bloom_end":"2025-05-20",
     "pest_name":"Aphids", "pest_start":"2025-04-05","pest_end":"2025-05-25"},
    {"flower": "Sunflower", "lat": 34.8, "lon": -81.0, "bloom_start":"2025-06-01","bloom_end":"2025-07-15",
     "pest_name":"Cucumber Beetle", "pest_start":"2025-06-10","pest_end":"2025-07-20"},
    {"flower": "Coneflower", "lat": 34.4, "lon": -81.3, "bloom_start":"2025-05-01","bloom_end":"2025-07-10",
     "pest_name":"Japanese Beetle", "pest_start":"2025-05-05","pest_end":"2025-07-15"},
]

df = pd.DataFrame(data)
df['bloom_start'] = pd.to_datetime(df['bloom_start'])
df['bloom_end'] = pd.to_datetime(df['bloom_end'])
df['pest_start'] = pd.to_datetime(df['pest_start'])
df['pest_end'] = pd.to_datetime(df['pest_end'])

# Flower icons (place PNGs in assets/)
flower_icons = {flower: f"/assets/{flower.lower().replace(' ','_')}.png" for flower in df['flower']}

# Initialize app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("SC Flower Bloom & Pest Tracker", style={"textAlign":"center"}),
    html.Div([
        html.Label("Select Flower:"),
        dcc.Dropdown(
            id='flower-dropdown',
            options=[{"label": f, "value": f} for f in df['flower'].unique()],
            value="Sunflower"
        )
    ], style={"width":"300px","margin":"auto"}),
    
    dl.Map(center=[34.0, -81.0], zoom=7, children=[
        dl.TileLayer(url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"),
        dl.LayerGroup(id="map-markers")
    ], style={'width': '100%', 'height': '500px'}, id="map"),
    
    dcc.Graph(id="bloom-graph")
])

# Callbacks
@app.callback(
    [Output("map-markers", "children"),
     Output("bloom-graph", "figure")],
    [Input("flower-dropdown", "value")]
)
def update_flower(flower_name):
    # Filter dataframe
    dff = df[df['flower'] == flower_name]
    
    # Create markers
    markers = []
    for _, row in dff.iterrows():
        icon_url = flower_icons.get(row['flower'], "/assets/default_flower.png")
        markers.append(
            dl.Marker(
                position=[row['lat'], row['lon']],
                icon=dl.Icon(iconUrl=icon_url, iconSize=[30,30], iconAnchor=[15,30]),
                children=[
                    dl.Tooltip(f"{row['flower']}"),
                    dl.Popup([
                        html.B(row['flower']),
                        html.Br(),
                        f"Pest: {row['pest_name']}",
                        html.Br(),
                        f"Bloom: {row['bloom_start'].date()} to {row['bloom_end'].date()}",
                        html.Br(),
                        f"Pest Active: {row['pest_start'].date()} to {row['pest_end'].date()}"
                    ])
                ]
            )
        )
    
    # Create bloom/pest figure
    fig = px.timeline(
        dff,
        x_start="bloom_start",
        x_end="bloom_end",
        y="flower",
        color_discrete_sequence=["orange"]
    )
    fig.add_bar(x=dff['pest_start'], y=dff['flower'], base=0, width=0.4, marker_color='red', name='Pest Active')
    fig.update_layout(yaxis={"categoryorder":"total ascending"}, title=f"{flower_name} Bloom & Pest Timeline")
    
    return markers, fig

if __name__ == "__main__":
    app.run(debug=True)
