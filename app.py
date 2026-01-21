# import streamlit as st
# import pandas as pd
# import xgboost as xgb

# # 1. Page Configuration
# st.set_page_config(page_title="🔥Wildfire Risk Portal", layout="wide")

# # 2. Loading the "Frozen" Model
# # Since it's a .ubj file, we initialize an empty XGBRegressor first
# model = xgb.XGBRegressor()
# model.load_model('fire_model_V1.ubj') # filename MUST match the set model_file_name

# # 3. Sidebar: Stakeholder Inputs
# st.sidebar.header("Fire Environment Parameters")
# st.sidebar.markdown("Adjust the sliders to simulate conditions.")

# target_month = st.sidebar.slider("Select Month", 1, 12, 1)
# ndvi = st.sidebar.slider("NDVI (Vegetation Health)", 0.0, 1.0, 0.3)
# lat = st.sidebar.number_input("Latitude (y)", value=1.40, format="%.8f")
# lon = st.sidebar.number_input("Longitude (x)", value=30.89, format="%.8f")

# # Simplified Confidence input for stakeholders
# conf_level = st.sidebar.selectbox("Satellite Confidence", ["High", "Nominal", "Low"])

# # 4. Process Inputs to match Training Data
# # Our model expects: [x, y, NDVI, MONTH, YEAR, CONFIDENCE_l, CONFIDENCE_n]
# # We map the stakeholder's choice back to our 0s and 1s
# conf_l = 1 if conf_level == "Low" else 0
# conf_n = 1 if conf_level == "Nominal" else 0

# # Create the exact same table structure the model was trained on
# input_data = pd.DataFrame([[lon, lat, ndvi, target_month, 2024, conf_l, conf_n]], 
#                            columns=['x', 'y', 'NDVI', 'MONTH', 'YEAR', 'CONFIDENCE_l', 'CONFIDENCE_n'])

# # 5. Main Display
# st.title("FIRE LENS - Wildfire Severity & Likelihood Portal")
# st.markdown("This portal uses Satellite imagery and Machine Learning to predict fire intensity.")

# # 6. Predict Logic
# if st.sidebar.button("Generate Prediction"):
#     prediction = model.predict(input_data)[0]
    
#     col1, col2 = st.columns([1, 2])
    
#     with col1:
#         st.subheader("Outcome")
#         # Defined Thresholds based on the training data
#         if prediction > 65:
#             st.error(f"### CRITICAL RISK\nPredicted Intensity: {prediction:.2f} K")
#             st.write("🔴 **Notification:** High likelihood of catastrophic fire. Deploy resources.")
#         elif prediction > 62:
#             st.warning(f"### MODERATE RISK\nPredicted Intensity: {prediction:.2f} K")
#             st.write("🟠 **Notification:** Seasonal drying detected. Heightened monitoring.")
#         else:
#             st.success(f"### STABLE\nPredicted Intensity: {prediction:.2f} K")
#             st.write("🟢 **Notification:** Conditions within normal safety range.")

#     with col2:
#         st.subheader("Location Awareness")
#         map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
#         st.map(map_data, zoom=10)

# # 7. Additional Contextual Information(reasoning)
#         st.subheader("Analysis Results")
#         if prediction > 65:
#             reason = ""
#             if ndvi < 0.2:
#                 reason += "Critical: Vegetation is extremely dry (Low NDVI). "
#             if target_month in [1, 2, 12]:
#                 reason += "Warning: This is the peak of the historical dry season."
#             st.info(f"**Reasoning:** {reason}")



# # --- 1. Page Config & Title ---
# st.set_page_config(page_title="FireLens Uganda", page_icon="🔥", layout="wide")
# st.title("FireLens: Wildfire Severity Portal")
# st.markdown("---")

# # --- 2. Load Model ---
# # Using the .ubj file you saved on my local PC
# model = xgb.XGBRegressor()
# model.load_model('fire_model_V1.ubj')  # Ensure this file is in the same model directory

# # --- 3. Sidebar Inputs (Restricted Range) ---
# st.sidebar.header("Input Controls")

# # Locked coordinate ranges based on your Uganda AOI training data
# lat = st.sidebar.slider("Latitude (y)", 0.0, 4.0, 1.40, help="Restricted to study area bounds")
# lon = st.sidebar.slider("Longitude (x)", 29.0, 35.0, 30.89, help="Restricted to study area bounds")

# st.sidebar.markdown("---")
# target_year = st.sidebar.selectbox("Prediction Year", [2024, 2025, 2026])
# target_month = st.sidebar.slider("Month", 1, 12, 1)
# ndvi = st.sidebar.slider("Vegetation Health (NDVI)", 0.0, 1.0, 0.3)

# # Background variables (Confidence set to Nominal/High)
# conf_l, conf_n = 0, 1

# # --- 4. Prediction Execution ---
# if st.sidebar.button("Run Risk Analysis"):
#     # Match the 7-column format from training
#     input_df = pd.DataFrame([[lon, lat, ndvi, target_month, target_year, conf_l, conf_n]], 
#                             columns=['x', 'y', 'NDVI', 'MONTH', 'YEAR', 'CONFIDENCE_l', 'CONFIDENCE_n'])
    
#     prediction = model.predict(input_df)[0]
    
#     # Layout Columns
#     col1, col2 = st.columns([1, 1])
    
#     with col1:
#         st.subheader("Severity Assessment")
#         if prediction > 65:
#             st.error(f"### ALERT: CRITICAL SEVERITY ({prediction:.2f} K)")
#         elif prediction > 62:
#             st.warning(f"### WARNING: MODERATE SEVERITY ({prediction:.2f} K)")
#         else:
#             st.success(f"### SAFE: LOW SEVERITY ({prediction:.2f} K)")

#         # --- THE REASONING ENGINE ---
#         st.info("#### Prediction Logic")
        
#         # Reason 1: Seasonality
#         if target_month in [1, 2, 12]:
#             st.write("**Seasonality:** High. We are in a historical dry window for this region.")
#         else:
#             st.write("**Seasonality:** Low/Moderate. Historically outside peak burning months.")
            
#         # Reason 2: Fuel Load (NDVI)
#         if ndvi < 0.2:
#             st.write("**Fuel State:** Critical. Vegetation is extremely dry/stressed.")
#         elif ndvi < 0.4:
#             st.write("**Fuel State:** Moderate. Vegetation is drying out.")
#         else:
#             st.write("**Fuel State:** Healthy. Moisture levels likely inhibit intense burning.")

#     with col2:
#         st.subheader("Regional Context")
#         # Displaying the map centered on the user's selection
#         map_df = pd.DataFrame({'lat': [lat], 'lon': [lon]})
#         st.map(map_df, zoom=7)



import streamlit as st
import pandas as pd
import numpy as np
import xgboost as xgb
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

# --- 1. Site Presets with Detailed Bounds ---
# (Lat, Lon, Buffer_Size)
SITES = {
    "Murchison Falls NP": (2.25, 31.79, 0.35),
    "Budongo Forest": (1.82, 31.59, 0.15),
    "Bugoma Forest": (1.26, 30.97, 0.15),
    "Kabwoya Wildlife Reserve": (1.49, 31.10, 0.10),
    "Kibale Forest (KCA)": (0.44, 30.37, 0.20)
}

MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4, 
    "May": 5, "June": 6, "July": 7, "August": 8, 
    "September": 9, "October": 10, "November": 11, "December": 12
}

# --- 2. Load Model ---
model = xgb.XGBRegressor()
model.load_model('fire_model_V1.ubj')  # Ensure this file is in the same model directory

# --- 3. Sidebar UI ---
st.sidebar.title("Albertine Rift Portal")

selected_name = st.sidebar.selectbox("Select Protected Area / AOI", list(SITES.keys()))
selected_month_name = st.sidebar.select_slider("Forecast Month", options=list(MONTH_MAP.keys()))
target_month = MONTH_MAP[selected_month_name]

ndvi_sim = st.sidebar.slider("Simulated NDVI (Vegetation Status)", 0.0, 1.0, 0.25)
st.sidebar.caption(" 0.25 represents typical dry-season vegetation.")

# --- 4. Heatmap Generation Engine ---
def get_aoi_predictions(lat, lon, buffer, ndvi, month):
    # Generates a grid over the park + community area
    lats = np.linspace(lat - buffer, lat + buffer, 25)
    lons = np.linspace(lon - buffer, lon + buffer, 25)
    data = []
    for lt in lats:
        for ln in lons:
            input_df = pd.DataFrame([[ln, lt, ndvi, month, 2026, 0, 1]], 
                                     columns=['x', 'y', 'NDVI', 'MONTH', 'YEAR', 'CONFIDENCE_l', 'CONFIDENCE_n'])
            pred = float(model.predict(input_df)[0])
            if pred > 61: # Only show 'Alert' level heat
                data.append([float(lt), float(ln), pred])
    return data

# --- 5. Main Map Interface ---
st.header(f"Fire Severity Forecast: {selected_name}")
st.subheader(f"Baseline for {selected_month_name} 2026")

site_lat, site_lon, site_buffer = SITES[selected_name]

# Create Map with "Hybrid" Detail (Labels + Satellite)
m = folium.Map(location=[site_lat, site_lon], zoom_start=11)

# Add Google Hybrid Tiles for Labels, Roads, and Features
folium.TileLayer(
    tiles = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
    attr = 'Google',
    name = 'Satellite with Labels',
    overlay = False,
    control = False
).add_to(m)

# # Highlight the AOI (The Park + Bordering Communities)
# folium.Rectangle(
#     bounds=[[site_lat - site_buffer, site_lon - site_buffer], 
#             [site_lat + site_buffer, site_lon + site_buffer]],
#     color="yellow",
#     weight=2,
#     fill=True,
#     fill_opacity=0.1,
#     popup="Active AOI (Park & Community Buffer)"
# ).add_to(m)

# Highlight the Park Core
folium.Rectangle(
    bounds=[[site_lat - site_buffer, site_lon - site_buffer], 
            [site_lat + site_buffer, site_lon + site_buffer]],
    color="darkgreen",
    weight=2,
    fill=False,
    popup="Protected Area Core"
).add_to(m)

# Highlight the Community Buffer (e.g., adding 0.05 degrees)
folium.Rectangle(
    bounds=[[site_lat - (site_buffer + 0.05), site_lon - (site_buffer + 0.05)], 
            [site_lat + (site_buffer + 0.05), site_lon + (site_buffer + 0.05)]],
    color="orange",
    dash_array='5, 5',
    weight=1,
    fill=True,
    fill_opacity=0.05,
    popup="Bordering Community Zone"
).add_to(m)

# Add the Risk Heatmap
heat_data = get_aoi_predictions(site_lat, site_lon, site_buffer, ndvi_sim, target_month)
if heat_data:
    HeatMap(heat_data, radius=15, blur=10, min_opacity=0.4).add_to(m)

st_folium(m, width="100%", height=600)

# --- 6. Summary for Stakeholders ---
st.markdown("---")
st.info(f"**Stakeholder Insight:** The heatmap above shows areas where thermal intensity is predicted to exceed 61K. "
        f"In **{selected_month_name}**, historical patterns for the Albertine Rift suggest { 'peak risk' if target_month in [1,2,12] else 'reduced risk' } "
        f"levels for {selected_name}.")