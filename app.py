import streamlit as st
import pandas as pd
import numpy as np
import xgboost as xgb
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import datetime

# Internal Module Imports
from config import SITES, MONTH_MAP, CURRENT_YEAR
from services.gee_service import get_live_ndvi
from services.nasa_service import fetch_nasa_fires
from utils.pdf_generator import create_pdf

# --- 1. SETUP ---
st.set_page_config(page_title="FireLens Uganda", layout="wide")
NASA_KEY = st.secrets['NASA_MAPKEY']

# Load XGBoost (The Brain)
@st.cache_resource
def load_model():
    m = xgb.XGBRegressor()
    m.load_model('assets/fire_model_V1.ubj') # Moved to assets folder
    return m

model = load_model()

# --- 2. SIDEBAR UI ---
st.sidebar.title("🛡️ FireLens Portal")
selected_site = st.sidebar.selectbox("Select Protected Area", list(SITES.keys()))
lat, lon, buffer, desc = SITES[selected_site]

map_snapshot = st.sidebar.file_uploader("Upload Map Snapshot", type=['png', 'jpg'])

# NDVI Logic (Live Sync)
if 'ndvi' not in st.session_state or st.session_state.get('last_site') != selected_site:
    with st.spinner("Syncing Satellite Data..."):
        st.session_state['ndvi'] = get_live_ndvi(lat, lon, buffer)
        st.session_state['last_site'] = selected_site

current_ndvi = st.sidebar.metric("Observed NDVI", st.session_state['ndvi'])
target_month = st.sidebar.select_slider("Forecast Month", options=list(MONTH_MAP.keys()))

# --- 3. DASHBOARD MAIN ---
eat_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
st.header(f"Dashboard: {selected_site}")
st.caption(f"Local Time: {eat_now.strftime('%Y-%m-%d %H:%M')} EAT")

# Map Generation
m = folium.Map(location=[lat, lon], zoom_start=11)
folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
                 attr='Google', name='Satellite').add_to(m)

# Fetch NASA Data
live_fires = fetch_nasa_fires(lat, lon, buffer, NASA_KEY)

# Display Map
if not live_fires.empty:
    for _, row in live_fires.iterrows():
        folium.CircleMarker([row['latitude'], row['longitude']], radius=8, color='red', fill=True).add_to(m)

st_folium(m, width="100%", height=500)

# --- 4. NAVIGATION & REPORTING ---
if not live_fires.empty:
    st.markdown("### 📍 Active Fire Navigation")
    # Clean table logic here... (omitted for brevity, same as previous version)
    st.dataframe(live_fires[['latitude', 'longitude', 'bright_ti4']])

# PDF Download
risk_level = "PEAK" if MONTH_MAP[target_month] in [1, 2, 12] else "REDUCED"
pdf_data = create_pdf(selected_site, st.session_state['ndvi'], risk_level, desc, live_fires, map_snapshot)
st.download_button("📄 Download Tactical Report", data=pdf_data, file_name="Report.pdf")