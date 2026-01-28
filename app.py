import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import datetime

# --- 1. INTERNAL MODULE IMPORTS ---
from config import SITES, MONTH_MAP, CURRENT_YEAR, AUTO_ALERT_ENABLED
from services.gee_service import get_live_ndvi
from services.nasa_service import fetch_nasa_fires
from services.model_service import load_xgb_model, get_aoi_predictions
from services.alert_service import evaluate_risk_level
from services.notification_service import send_telegram_alert
from utils.pdf_generator import create_pdf

# --- 2. SETUP & INITIALIZATION ---
st.set_page_config(page_title="FireLens Uganda", layout="wide")
NASA_KEY = st.secrets['NASA_MAPKEY']

# Load the model once (Cached)
model = load_xgb_model()

# --- 3. SIDEBAR UI (Gather Inputs First) ---
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
target_month_name = st.sidebar.select_slider("Forecast Month", options=list(MONTH_MAP.keys()))
target_month = MONTH_MAP[target_month_name]

# --- 4. DATA PROCESSING (The "Brain" Work) ---
# Now that we have inputs, we run the model and fetch NASA data
with st.spinner("Analyzing terrain risk..."):
    # Generate Heatmap Predictions
    heat_data = get_aoi_predictions(model, lat, lon, buffer, st.session_state['ndvi'], target_month)
    
    # Fetch NASA Live Fire Data
    live_fires = fetch_nasa_fires(lat, lon, buffer, NASA_KEY)
    
    # Evaluate Risk Levels for Alerting
    risk_level, alert_msgs, is_dispatch_worthy = evaluate_risk_level(
        st.session_state['ndvi'], 
        heat_data, 
        live_fires
    )

# --- 5. DASHBOARD HEADER ---
eat_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
st.header(f"Dashboard: {selected_site}")
st.caption(f"Local Time: {eat_now.strftime('%Y-%m-%d %H:%M')} EAT")

# --- 6. VISUALIZATION (Map & Tables) ---
col_left, col_right = st.columns([2, 1])

with col_left:
    # Map Generation
    m = folium.Map(location=[lat, lon], zoom_start=11)
    folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
                     attr='Google', name='Satellite').add_to(m)

    # Add AI Heatmap
    if heat_data:
        HeatMap(heat_data, radius=15, blur=8, min_opacity=0.5).add_to(m)

    # Add NASA Live Points
    if not live_fires.empty:
        for _, row in live_fires.iterrows():
            folium.CircleMarker(
                [row['latitude'], row['longitude']], 
                radius=8, color='red', fill=True, 
                popup=f"Intensity: {row['bright_ti4']}K"
            ).add_to(m)

    st_folium(m, width="100%", height=500)

with col_right:
    # Display Alert Banner
    if risk_level != "NORMAL":
        st.error(f"### ⚠️ {risk_level} RISK")
        for msg in alert_msgs:
            st.write(f"- {msg}")
    else:
        st.success("✅ Risk levels are normal.")

    # Table for Navigation
    if not live_fires.empty:
        st.markdown("### 📍 Active Points")
        st.dataframe(live_fires[['latitude', 'longitude', 'bright_ti4']], use_container_width=True)

# --- 7. ACTIONS (Reporting & Notifications) ---
st.markdown("---")
c1, c2 = st.columns(2)

with c1:
    # PDF Download
    risk_label = "PEAK" if target_month in [1, 2, 12] else "REDUCED"
    pdf_data = create_pdf(selected_site, st.session_state['ndvi'], risk_label, desc, live_fires, map_snapshot)
    st.download_button("📄 Download Tactical Report", data=pdf_data, file_name=f"FireLens_{selected_site}.pdf")

with c2:
    # AUTOMATIC DISPATCH LOGIC
    if AUTO_ALERT_ENABLED and is_dispatch_worthy:
        sent_key = f"sent_{selected_site}_{datetime.date.today()}"
        if sent_key not in st.session_state:
            with st.status("🚀 Critical Risk! Auto-dispatching Telegram...", expanded=False):
                success, info = send_telegram_alert(selected_site, risk_level, alert_msgs)
                if success:
                    st.session_state[sent_key] = True
                    st.toast("✅ Auto-Alert Sent to Rangers", icon="📢")
                else:
                    st.error(f"Auto-dispatch failed: {info}")

    # Manual Fallback
    if st.button("📢 Manual Broadcast (Resend)"):
        send_telegram_alert(selected_site, risk_level, alert_msgs)
        st.toast("Manual alert dispatched.")