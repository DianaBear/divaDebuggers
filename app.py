
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
# app.py



# app.py
import dash
from dash import dcc, html, Input, Output
import dash_leaflet as dl
import pandas as pd
import numpy as np
import plotly.express as px

# ---------- FLOWERS & PESTS ----------
flowers = ["Sunflower", "Daisy", "Rose", "Lily", "Tulip"]
pests = {
    "Sunflower": ["Beetle", "Aphid"],
    "Daisy": ["Caterpillar", "Moth"],
    "Rose": ["Thrips", "Aphid"],
    "Lily": ["Moth", "Beetle"],
    "Tulip": ["Thrips", "Caterpillar"]
}

# ---------- HARD-CODED COORDINATES (spread across SC) ----------
flower_coords = {
    "Sunflower": [
        (33.95,-81.0),(34.0,-80.9),(34.05,-81.1),(33.9,-80.95),(34.1,-81.05),
        (34.15,-81.0),(33.85,-80.98),(34.07,-80.97),(33.92,-81.02),(34.02,-81.04),
        (33.97,-80.93),(34.06,-81.07),(33.88,-80.99),(34.03,-81.01),(33.96,-81.05),
        (33.91,-81.03),(34.08,-80.96),(33.99,-81.06),(34.04,-80.92),(33.93,-80.97),
        (33.89,-81.04),(34.05,-81.02),(33.94,-81.01),(34.01,-80.99),(33.98,-81.03)
    ],
    "Daisy": [
        (34.2,-81.1),(34.1,-81.0),(34.05,-80.95),(34.15,-81.05),(34.0,-80.9),
        (34.12,-81.02),(34.08,-81.03),(34.03,-80.97),(34.06,-81.04),(34.07,-81.06),
        (34.09,-81.05),(34.11,-80.98),(34.0,-81.01),(34.04,-81.02),(34.02,-81.03),
        (34.05,-80.96),(34.01,-81.07),(34.03,-81.0),(34.08,-81.01),(34.06,-81.03),
        (34.12,-80.97),(34.09,-81.06),(34.07,-80.99),(34.0,-81.04),(34.1,-81.03)
    ],
    "Rose": [
        (33.8,-81.2),(33.85,-81.15),(33.82,-81.18),(33.87,-81.1),(33.83,-81.12),
        (33.9,-81.14),(33.88,-81.16),(33.86,-81.11),(33.89,-81.09),(33.84,-81.13),
        (33.91,-81.12),(33.87,-81.08),(33.85,-81.09),(33.9,-81.1),(33.88,-81.07),
        (33.83,-81.06),(33.92,-81.15),(33.81,-81.12),(33.86,-81.13),(33.84,-81.08),
        (33.89,-81.14),(33.82,-81.11),(33.91,-81.09),(33.85,-81.1),(33.87,-81.07)
    ],
    "Lily": [
        (34.0,-80.8),(34.05,-80.85),(34.02,-80.82),(34.03,-80.87),(34.01,-80.83),
        (34.04,-80.88),(34.06,-80.81),(34.07,-80.86),(34.08,-80.84),(34.05,-80.82),
        (34.03,-80.83),(34.02,-80.85),(34.06,-80.88),(34.01,-80.84),(34.07,-80.82),
        (34.0,-80.86),(34.05,-80.83),(34.08,-80.81),(34.04,-80.85),(34.02,-80.87),
        (34.03,-80.84),(34.06,-80.82),(34.01,-80.88),(34.07,-80.83),(34.08,-80.86)
    ],
    "Tulip": [
        (33.95,-80.7),(34.0,-80.75),(33.92,-80.72),(33.97,-80.78),(33.93,-80.74),
        (33.98,-80.71),(33.96,-80.79),(33.99,-80.73),(33.91,-80.77),(33.94,-80.76),
        (33.95,-80.72),(33.97,-80.75),(33.92,-80.78),(33.98,-80.74),(33.93,-80.79),
        (33.96,-80.71),(33.99,-80.76),(33.94,-80.73),(33.91,-80.75),(33.95,-80.78),
        (33.97,-80.72),(33.92,-80.74),(33.98,-80.76),(33.96,-80.73),(33.99,-80.71)
    ]
}

# ---------- CREATE DATAFRAME ----------
records = []
for flower in flowers:
    coords = flower_coords[flower]
    for lat, lon in coords:
        ndvi = 0.3 + 0.5 * np.random.rand()
        bloom = ndvi > 0.5
