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
import xgboost as xgb
import folium
from streamlit_folium import st_folium

# --- 1. Conservation Site Presets ---
SITES = {
    "Murchison Falls National Park": (2.2500, 31.7900, "Savanna/Woodland"),
    "Budongo Central Forest Reserve": (1.8200, 31.5900, "Tropical High Forest"),
    "Bugoma Central Forest Reserve": (1.2600, 30.9700, "Tropical High Forest"),
    "Kabwoya Wildlife Reserve": (1.4934, 31.1032, "Rift Escarpment/Savanna"),
    "Kibale Forest (KCA)": (0.4364, 30.3667, "Evergreen/Primate Habitat")
}

# --- 2. Load Model & Setup ---
st.set_page_config(layout="wide", page_title="Albertine Rift FireLens")
model = xgb.XGBRegressor()
model.load_model('fire_model_V1.ubj')

# --- 3. Sidebar: Regional Controls ---
st.sidebar.header("Albertine Rift Navigation")
selected_name = st.sidebar.selectbox("Choose Protected Area", list(SITES.keys()))
site_lat, site_lon, ecosystem = SITES[selected_name]

st.sidebar.markdown(f"**Ecosystem:** {ecosystem}")
st.sidebar.divider()

# Forecast Inputs
target_month = st.sidebar.slider("Forecast Month", 1, 12, 1)
ndvi_val = st.sidebar.slider("Simulated NDVI (Greenness)", 0.0, 1.0, 0.3)

# --- 4. Main Interactive Map ---
st.title(f"📍 Analysis: {selected_name}")
st.write(f"This portal predicts fire intensity based on historical patterns in the {ecosystem} ecosystem.")

m = folium.Map(location=[site_lat, site_lon], zoom_start=11, 
               tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
               attr="Esri World Imagery")

# Add a marker for the site center
folium.Marker([site_lat, site_lon], popup=f"Center of {selected_name}", icon=folium.Icon(color='blue')).add_to(m)

# Execute the map and capture clicks
map_output = st_folium(m, width="100%", height=500)

# --- 5. Prediction Engine ---
# Use either the preset center or a specific point the user clicked
active_lat = map_output['last_clicked']['lat'] if map_output['last_clicked'] else site_lat
active_lon = map_output['last_clicked']['lng'] if map_output['last_clicked'] else site_lon

input_df = pd.DataFrame([[active_lon, active_lat, ndvi_val, target_month, 2026, 0, 1]], 
                         columns=['x', 'y', 'NDVI', 'MONTH', 'YEAR', 'CONFIDENCE_l', 'CONFIDENCE_n'])

prediction = model.predict(input_df)[0]

# --- 6. Results Panel (NASA Worldview Style) ---
res_col1, res_col2 = st.columns([1, 2])
with res_col1:
    st.metric("Predicted Severity", f"{prediction:.2f} K")
    if prediction > 65:
        st.error("🔥 STATUS: CRITICAL RISK")
    elif prediction > 62:
        st.warning("⚠️ STATUS: MODERATE RISK")
    else:
        st.success("✅ STATUS: LOW RISK")

with res_col2:
    st.info(f"**Site Context for {selected_name}:**")
    st.write(f"- **Latitude/Longitude:** `{active_lat:.4f}, {active_lon:.4f}`")
    st.write(f"- **Vegetation Status:** NDVI of {ndvi_val} indicates {'stressed/dry' if ndvi_val < 0.3 else 'healthy'} biomass.")
    st.write(f"- **Historical Context:** In Month {target_month}, {selected_name} typically shows { 'high' if target_month in [1,2,12] else 'low' } thermal activity.")