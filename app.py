import streamlit as st
import pandas as pd
import numpy as np
import xgboost as xgb
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from fpdf import FPDF
import io
import requests
import ee
import datetime
from PIL import Image
import os

# --- 0. Page Config (Wide Mode for Tactical View) ---
st.set_page_config(page_title="FireLens Uganda", layout="wide")

# --- 1. Configurations & GEE Initialization ---
NASA_MAPKEY = st.secrets['NASA_MAPKEY']

def initialize_gee():
    try:
        ee.data.getAssetStats('projects/earthengine-public/assets/COPERNICUS/S2_SR_HARMONIZED')
    except Exception:
        try:
            gee_json = st.secrets["gee_service_account"]
            credentials = ee.ServiceAccountCredentials(
                gee_json['client_email'], 
                key_data=gee_json['private_key']
            )
            ee.Initialize(credentials)
        except Exception as e:
            st.error(f"GEE Initialization Failed: {e}")
            st.stop()

# --- 2. GEE Satellite Logic ---
def mask_s2_clouds(image):
    qa = image.select('QA60')
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
    return image.updateMask(mask).divide(10000)

def get_live_ndvi(lat, lon, buffer_deg):
    initialize_gee()
    point = ee.Geometry.Point([lon, lat]).buffer(buffer_deg * 111000)
    # Use GMT+3 for time filtering
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    start_date = (now - datetime.timedelta(days=60)).strftime('%Y-%m-%d')
    collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                  .filterBounds(point)
                  .filterDate(start_date, now.strftime('%Y-%m-%d'))
                  .map(mask_s2_clouds))
    composite = collection.median()
    ndvi = composite.normalizedDifference(['B8', 'B4']).rename('NDVI')
    stats = ndvi.reduceRegion(reducer=ee.Reducer.mean(), geometry=point, scale=30, maxPixels=1e9)
    res = stats.get('NDVI').getInfo()
    return res if res is not None else 0.25

# --- 3. Resource Loading ---
@st.cache_resource
def load_xgb_model():
    model = xgb.XGBRegressor()
    model.load_model('fire_model_V1.ubj')
    return model

model = load_xgb_model()

# --- 4. NASA FIRMS Live Data Fetcher ---
@st.cache_data(ttl=3600)
def fetch_nasa_fires(lat, lon, buffer):
    west, south = lon - buffer, lat - buffer
    east, north = lon + buffer, lat + buffer
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{NASA_MAPKEY}/VIIRS_SNPP_NRT/{west},{south},{east},{north}/1"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return pd.read_csv(io.StringIO(response.text))
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- 5. Prediction & PDF Engines ---
@st.cache_data
def get_aoi_predictions(_model, lat, lon, buffer, ndvi, month):
    lats = np.linspace(lat - buffer, lat + buffer, 25)
    lons = np.linspace(lon - buffer, lon + buffer, 25)
    data = []
    for lt in lats:
        for ln in lons:
            input_df = pd.DataFrame([[ln, lt, ndvi, month, 2026, 0, 1]], 
                                     columns=['x', 'y', 'NDVI', 'MONTH', 'YEAR', 'CONFIDENCE_l', 'CONFIDENCE_n'])
            pred = float(_model.predict(input_df)[0])
            if pred > 61: 
                data.append([float(lt), float(ln), pred])
    return data

def create_pdf(site, month, ndvi, risk, description, live_fires_df, map_image=None):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(200, 10, txt="FireLens Uganda: Tactical Operational Report", ln=True, align='C')
    pdf.ln(10)
    
    # Localized Time
    eat_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    
    # Metadata
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, txt=f"AREA AUDIT: {site}", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 7, txt=f"Timestamp: {eat_time.strftime('%Y-%m-%d %H:%M')} GMT+3 (EAT)", ln=True)
    pdf.cell(0, 7, txt=f"Satellite NDVI: {ndvi} | Forecast Risk: {risk}", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 7, txt=f"Site Context: {description}")
    pdf.ln(5)

    # 1. Map Image Integration
    if map_image is not None:
        # Save temp image for PDF insertion
        img = Image.open(map_image)
        temp_path = "map_snapshot.png"
        img.save(temp_path)
        pdf.image(temp_path, x=10, y=None, w=190)
        pdf.ln(5)
        if os.path.exists(temp_path):
            os.remove(temp_path)
    else:
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 10, txt="[No tactical map snapshot attached]", ln=True)

    # 2. Live Detections Section
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, txt="TACTICAL FIRE COORDINATES", ln=True, fill=True)
    pdf.ln(2)

    if not live_fires_df.empty:
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(35, 7, "Latitude", 1); pdf.cell(35, 7, "Longitude", 1)
        pdf.cell(30, 7, "Intensity (K)", 1); pdf.cell(40, 7, "Priority", 1)
        pdf.ln()
        
        pdf.set_font("Arial", size=9)
        for _, row in live_fires_df.iterrows():
            priority = "HIGH" if row['bright_ti4'] >= 330 else "Standard"
            pdf.cell(35, 7, str(round(row['latitude'], 5)), 1)
            pdf.cell(35, 7, str(round(row['longitude'], 5)), 1)
            pdf.cell(30, 7, str(row['bright_ti4']), 1)
            pdf.cell(40, 7, priority, 1)
            pdf.ln()
    
    return bytes(pdf.output())

# --- 6. Sidebar UI ---
SITES = {
    "Murchison Falls NP": (2.25, 31.79, 0.35, "Savanna/Woodland mosaic. High fuel load."),
    "Budongo Forest": (1.82, 31.59, 0.15, "Tropical High Forest. Primate habitat."),
    "Bugoma Forest": (1.26, 30.97, 0.15, "Tropical High Forest. Community edge risk."),
    "Kabwoya Wildlife Reserve": (1.49, 31.10, 0.10, "Rift Escarpment. Steep terrain."),
    "Kibale Forest (KCA)": (0.44, 30.37, 0.20, "Moist Evergreen. Primate density.")
}

MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
}

st.sidebar.title("🛡️ FireLens Portal")
selected_name = st.sidebar.selectbox("Select Protected Area", list(SITES.keys()))
site_lat, site_lon, site_buffer, site_desc = SITES[selected_name]

st.sidebar.markdown("---")
st.sidebar.subheader("📸 Operational Snapshot")
# Added feature for PDF Screenshot
map_snapshot = st.sidebar.file_uploader("Upload Map Screenshot for Report", type=['png', 'jpg', 'jpeg'])

st.sidebar.markdown("---")
st.sidebar.subheader("🛰️ Satellite NDVI Control")
data_mode = st.sidebar.radio("Data Source", ["Live Sentinel-2 (Auto-Sync)", "Manual Simulation"])

if data_mode == "Live Sentinel-2 (Auto-Sync)":
    if 'last_site' not in st.session_state or st.session_state['last_site'] != selected_name:
        with st.spinner(f"Syncing Sentinel-2 (GMT+3)..."):
            val = get_live_ndvi(site_lat, site_lon, site_buffer)
            st.session_state['live_ndvi'] = round(val, 3)
            st.session_state['last_site'] = selected_name
    current_ndvi = st.session_state.get('live_ndvi', 0.25)
    st.sidebar.metric("Live Observed NDVI", current_ndvi)
else:
    current_ndvi = st.sidebar.slider("Simulated NDVI", 0.0, 1.0, 0.25)

selected_month_name = st.sidebar.select_slider("Forecast Month", options=list(MONTH_MAP.keys()))
target_month = MONTH_MAP[selected_month_name]
show_nasa = st.sidebar.checkbox("Show NASA Live Fires (24h)", value=True)

# --- 7. Main Map Interface ---
eat_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
st.header(f"Operational Dashboard: {selected_name}")
st.subheader(f"Current Condition: {eat_now.strftime('%H:%M')} EAT | NDVI {current_ndvi}")

live_fires = pd.DataFrame()

with st.spinner("Updating prediction layers..."):
    m = folium.Map(location=[site_lat, site_lon], zoom_start=11)
    folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
                     attr='Google', name='Satellite Labels').add_to(m)

    heat_data = get_aoi_predictions(model, site_lat, site_lon, site_buffer, current_ndvi, target_month)
    if heat_data:
        HeatMap(heat_data, radius=15, blur=8, min_opacity=0.5,
                gradient={0.4: 'blue', 0.65: 'yellow', 0.85: 'orange', 1.0: 'red'}).add_to(m)

    if show_nasa:
        live_fires = fetch_nasa_fires(site_lat, site_lon, site_buffer)
        if not live_fires.empty:
            for _, row in live_fires.iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=9, color='red', fill=True, fill_color='orange',
                    popup=f"Intensity: {row['bright_ti4']}K"
                ).add_to(m)

    folium.Rectangle(bounds=[[site_lat-site_buffer, site_lon-site_buffer], 
                             [site_lat+site_buffer, site_lon+site_buffer]],
                     color="darkgreen", weight=2, fill=False).add_to(m)
    
    st_folium(m, width="100%", height=550)

# --- 8. Tactical Detection Table with Google Maps Links ---
if not live_fires.empty:
    st.markdown("### 📍 Active Fire Navigation Table")
    
    table_data = live_fires[['latitude', 'longitude', 'bright_ti4', 'acq_time']].copy()
    
    # Priority Logic
    table_data['Priority'] = table_data['bright_ti4'].apply(lambda x: "🚨 HIGH" if x >= 330 else "⚠️ Standard")
    
    # 3. Google Maps Link Generation
    table_data['Google Maps'] = table_data.apply(
        lambda row: f"https://www.google.com/maps?q={row['latitude']},{row['longitude']}", axis=1
    )
    
    # Reorder and Rename
    table_data = table_data[['Priority', 'latitude', 'longitude', 'bright_ti4', 'acq_time', 'Google Maps']]
    table_data.columns = ['Status', 'Lat', 'Lon', 'Intensity (K)', 'Time (UTC)', 'Navigation Link']

    st.dataframe(
        table_data,
        column_config={
            "Navigation Link": st.column_config.LinkColumn("Open in Maps")
        },
        use_container_width=True,
        hide_index=True
    )
elif show_nasa:
    st.info("No active thermal anomalies detected in the last 24 hours.")

# --- 9. Reporting ---
st.markdown("---")
risk_level = "PEAK" if target_month in [1, 2, 12] else "REDUCED"
col1, col2 = st.columns(2)
with col1:
    st.info(f"**Site Profile:** {site_desc}")
with col2:
    # Pass map_snapshot to the PDF generator
    pdf_output = create_pdf(selected_name, selected_month_name, current_ndvi, risk_level, site_desc, live_fires, map_snapshot)
    st.download_button(label="Download Risk Report (PDF)", data=pdf_output, 
                       file_name=f"FireLens_Report_{selected_name}.pdf", mime="application/pdf")

st.caption("Data: NASA FIRMS (Live) | Google Earth Engine (Live NDVI) | XGBoost (Predictive)")