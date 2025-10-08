
# app.py
import dash
from dash import dcc, html, Input, Output
import dash_leaflet as dl
import pandas as pd
import numpy as np
import plotly.express as px

# ---------- FAKE DATA ----------
dates = pd.date_range(start="2025-01-01", end="2025-12-31", freq="7D")
num_points = len(dates)

flowers = ["Sunflower", "Daisy", "Rose", "Lily", "Tulip"]
pests = {
    "Sunflower": ["Beetle", "Aphid"],
    "Daisy": ["Caterpillar", "Moth"],
    "Rose": ["Thrips", "Aphid"],
    "Lily": ["Moth", "Beetle"],
    "Tulip": ["Thrips", "Caterpillar"]
}

# Generate dataset
data = {
    "date": dates,
    "flower": np.random.choice(flowers, size=num_points),
    "ndvi": np.random.uniform(0.3, 0.8, size=num_points),
    "lat": np.random.uniform(32, 35, size=num_points),
    "lon": np.random.uniform(-83, -78, size=num_points)
}

df = pd.DataFrame(data)
df["bloom"] = df["ndvi"] > 0.5  # NDVI threshold for bloom

# Add pest info based on flower
def assign_pest(row):
    flower = row["flower"]
    if row["bloom"]:
        return np.random.choice(pests[flower])
    else:
        return "No pests"

df["common_pest"] = df.apply(assign_pest, axis=1)

# ---------- DASH APP ----------
app = dash.Dash(__name__)
app.title = "Bloom & Pest Tracker SC"

app.layout = html.Div([
    html.H1("Bloom & Pest Tracker SC", style={"textAlign": "center", "color": "white"}),

    html.Div([
        html.Label("Select Flower:", style={"color": "white"}),
        dcc.Dropdown(
            id="flower-dropdown",
            options=[{"label": f, "value": f} for f in flowers],
            value="Sunflower",
            style={"width": "300px"}
        )
    ], style={"width": "300px", "margin": "auto"}),

    html.Div(dl.Map(center=[33.5, -80.5], zoom=7, id="bloom-map", style={"width": "100%", "height": "500px"})),
    html.Div(dcc.Graph(id="bloom-graph"))
], style={"backgroundColor": "#0B3D91", "padding": "20px"})

# ---------- CALLBACK ----------
@app.callback(
    Output("bloom-map", "children"),
    Output("bloom-graph", "figure"),
    Input("flower-dropdown", "value")
)
def update_flower(flower_name):
    df_filtered = df[df["flower"] == flower_name]

    # --- Map markers ---
    markers = [
        dl.Marker(
            position=[row["lat"], row["lon"]],
            children=dl.Popup(html.Div([
                html.B(f"{row['flower']}"),
                html.Br(),
                f"Bloom: {'Yes' if row['bloom'] else 'No'}",
                html.Br(),
                f"Pest: {row['common_pest']}"
            ]))
        )
        for i, row in df_filtered.iterrows()
    ]

    tile_layer = dl.TileLayer(url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")

    # --- Graph ---
    fig = px.line(df_filtered, x="date", y="ndvi", title=f"{flower_name} NDVI & Bloom Periods",
                  labels={"ndvi": "NDVI"})
    fig.add_scatter(x=df_filtered[df_filtered["bloom"]]["date"],
                    y=df_filtered[df_filtered["bloom"]]["ndvi"],
                    mode="markers",
                    marker=dict(color="orange", size=10),
                    name="Bloom")
    fig.update_layout(plot_bgcolor="#0B3D91", paper_bgcolor="#0B3D91", font_color="white")

    return [tile_layer] + markers, fig

# ---------- RUN APP ----------
if __name__ == "__main__":
    app.run(debug=True)
app.py

