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
# New UI components for tactical styling
from utils.ui_components import inject_custom_css, display_risk_banner

# --- 2. SETUP & INITIALIZATION ---
st.set_page_config(
    page_title="FireLens Uganda | Tactical Command",
    page_icon="🛡️",
    layout="wide"
)

# Apply custom dark-themed CSS styling
inject_custom_css()

# API Keys and Model Loading
NASA_KEY = st.secrets['NASA_MAPKEY']
model = load_xgb_model()

# --- 3. SIDEBAR UI (Input & Configuration) ---
with st.sidebar:
    st.title("🛡️ FireLens Portal")
    st.subheader("Tactical Configuration")
    
    selected_site = st.selectbox("🎯 Target Protected Area", list(SITES.keys()))
    lat, lon, buffer, desc = SITES[selected_site]
    
    st.divider()
    
    # Forecast controls for XGBoost temporal features
    target_month_name = st.select_slider("Forecast Month", options=list(MONTH_MAP.keys()))
    target_month = MONTH_MAP[target_month_name]
    
    st.divider()
    
    # Image upload for inclusion in the PDF tactical report
    map_snapshot = st.sidebar.file_uploader("Upload Map Snapshot", type=['png', 'jpg'])
    
    st.divider()
    st.caption(f"System Status: Operational")
    st.caption(f"v1.2.0 | © 2026 FireLens")

# --- 4. DATA SYNCHRONIZATION (The Logic Core) ---
# We manage the NDVI sync here to ensure it only updates when the site changes
if 'ndvi' not in st.session_state or st.session_state.get('last_site') != selected_site:
    with st.spinner("🛰️ Syncing Satellite Fuel Data..."):
        st.session_state['ndvi'] = get_live_ndvi(lat, lon, buffer)
        st.session_state['last_site'] = selected_site

# Run background processing for Predictions and NASA fetches
with st.spinner("🧠 Processing spatial intelligence..."):
    # AI Prediction Grid
    heat_data = get_aoi_predictions(model, lat, lon, buffer, st.session_state['ndvi'], target_month)
    
    # Live Thermal Anomalies
    live_fires = fetch_nasa_fires(lat, lon, buffer, NASA_KEY)
    
    # Multi-factor Risk Evaluation
    risk_level, alert_msgs, is_dispatch_worthy = evaluate_risk_level(
        st.session_state['ndvi'], 
        heat_data, 
        live_fires
    )

# --- 5. TOP-LEVEL METRIC DASHBOARD ---
# Provides immediate situational awareness before diving into the map
eat_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
st.title(f"📍 {selected_site}")
st.caption(f"Operational Briefing • {eat_now.strftime('%Y-%m-%d %H:%M')} EAT")

m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("Vegetation NDVI", st.session_state['ndvi'])
m_col2.metric("Active Fires", len(live_fires))
m_col3.metric("AI Confidence", f"{round(max([p[2] for p in heat_data]), 1) if heat_data else 0}%")
m_col4.metric("Risk Status", risk_level)

st.divider()

# --- 6. TACTICAL TABS (UX Separation) ---
tab_map, tab_analytics, tab_dispatch = st.tabs(["🗺️ Tactical Map", "📊 Analysis & Navigation", "📢 Dispatch Center"])

with tab_map:
    # High-visibility pulsing banner for risk status
    display_risk_banner(risk_level, alert_msgs)
    
    # Map Generation - Focus on Full Width
    m = folium.Map(location=[lat, lon], zoom_start=11, tiles=None)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
        attr='Google', name='Satellite Labels', overlay=False, control=True
    ).add_to(m)

    # AI Predictive Heatmap Layer
    if heat_data:
        HeatMap(heat_data, radius=15, blur=8, min_opacity=0.4).add_to(m)

    # NASA Real-time Fire Markers
    if not live_fires.empty:
        for _, row in live_fires.iterrows():
            folium.CircleMarker(
                [row['latitude'], row['longitude']], 
                radius=10, color='#ff4b4b', fill=True, fill_opacity=0.7,
                popup=f"Intensity: {row['bright_ti4']}K"
            ).add_to(m)

    st_folium(m, width="100%", height=600, returned_objects=[])

with tab_analytics:
    a_col1, a_col2 = st.columns([1, 2])
    with a_col1:
        st.subheader("Site Context")
        st.info(desc)
        
        # PDF Generation & Download
        risk_label = "PEAK" if target_month in [1, 2, 12] else "REDUCED"
        pdf_data = create_pdf(selected_site, st.session_state['ndvi'], risk_label, desc, live_fires, map_snapshot)
        st.download_button(
            "📄 Export Tactical PDF Report", 
            data=pdf_data, 
            file_name=f"FireLens_{selected_site}_{datetime.date.today()}.pdf",
            use_container_width=True
        )

    with a_col2:
        st.subheader("Target Coordinates (NASA VIIRS)")
        if not live_fires.empty:
            # Table showing coordinates for field deployment
            st.dataframe(
                live_fires[['latitude', 'longitude', 'bright_ti4', 'acq_time']], 
                use_container_width=True,
                hide_index=True
            )
        else:
            st.write("No active thermal anomalies detected in this AOI.")

with tab_dispatch:
    st.subheader("Communication & Notification Control")
    
    # Automatic Dispatch Feedback
    if AUTO_ALERT_ENABLED and is_dispatch_worthy:
        sent_key = f"sent_{selected_site}_{datetime.date.today()}"
        if sent_key not in st.session_state:
            with st.status("🚀 Automatic High-Risk Dispatch in progress...", expanded=False):
                success, info = send_telegram_alert(selected_site, risk_level, alert_msgs)
                if success:
                    st.session_state[sent_key] = True
                    st.toast("Auto-Alert Broadcasted!", icon="📢")
                else:
                    st.error(f"Dispatch Error: {info}")
        else:
            st.success("✅ Automatic alert for today has already been broadcasted to the Ranger Group.")

    st.divider()
    
    # Manual Override
    st.write("Force a manual update to the field teams:")
    if st.button("📢 Manual Broadcast (Telegram)", use_container_width=True):
        success, info = send_telegram_alert(selected_site, risk_level, alert_msgs)
        if success:
            st.toast("Manual alert dispatched successfully.")
        else:
            st.error(f"Manual dispatch failed: {info}")