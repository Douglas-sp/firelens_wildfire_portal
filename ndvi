import streamlit as st
import pandas as pd
import numpy as np
import xgboost as xgb
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

# --- Load Model ---
model = xgb.XGBRegressor()
model.load_model('your_model_name.ubj')

# --- Site Presets (Lat, Lon, Radius in degrees) ---
SITES = {
    "Murchison Falls NP": (2.25, 31.79, 0.4),
    "Budongo Forest": (1.82, 31.59, 0.2),
    "Bugoma Forest": (1.26, 30.97, 0.2),
    "Kabwoya Wildlife Reserve": (1.49, 31.10, 0.15),
    "Kibale Forest (KCA)": (0.43, 30.36, 0.25)
}

st.sidebar.header("Heatmap Settings")
selected_name = st.sidebar.selectbox("Select Protected Area", list(SITES.keys()))
ndvi_sim = st.sidebar.slider("Simulated NDVI (Dryness)", 0.0, 1.0, 0.25)
target_month = st.sidebar.slider("Month", 1, 12, 1)

# --- 3. The Heatmap Engine ---
def generate_heatmap_data(lat, lon, radius, ndvi, month):
    # Create a grid of 400 points (20x20) around the site
    lats = np.linspace(lat - radius, lat + radius, 20)
    lons = np.linspace(lon - radius, lon + radius, 20)
    
    grid_points = []
    for lt in lats:
        for ln in lons:
            # Format: [x, y, NDVI, MONTH, YEAR, CONF_L, CONF_N]
            input_data = pd.DataFrame([[ln, lt, ndvi, month, 2026, 0, 1]], 
                                       columns=['x', 'y', 'NDVI', 'MONTH', 'YEAR', 'CONFIDENCE_l', 'CONFIDENCE_n'])
            pred = model.predict(input_data)[0]
            
            # We only show high-intensity points on the heatmap (NASA FIRMS Style)
            if pred > 60: 
                grid_points.append([lt, ln, pred])
    return grid_points

# --- 4. Render the Portal ---
st.title(f"🔥 {selected_name} Risk Heatmap")
st.write(f"Showing predicted thermal anomalies for Month {target_month} at {ndvi_sim} NDVI.")

site_lat, site_lon, site_radius = SITES[selected_name]
heatmap_data = generate_heatmap_data(site_lat, site_lon, site_radius, ndvi_sim, target_month)

# Create the Map
m = folium.Map(location=[site_lat, site_lon], zoom_start=10, tiles="cartodbpositron")

# Add the Heatmap Layer (Windy style)
if heatmap_data:
    HeatMap(heatmap_data, radius=15, blur=10, min_opacity=0.5).add_to(m)
else:
    st.info("Conditions are currently too stable to generate risk heat.")

st_folium(m, width=1000, height=500)