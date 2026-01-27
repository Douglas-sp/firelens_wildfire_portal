import streamlit as st
import pandas as pd
import numpy as np
import xgboost as xgb
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from fpdf import FPDF
import io
import requests  # Required for NASA API calls

# --- 1. Configurations & Site Presets ---
NASA_MAPKEY = st.secrets['NASA_MAPKEY']

SITES = {
    "Murchison Falls NP": (2.25, 31.79, 0.35, "Savanna/Woodland mosaic. High fuel load in dry seasons."),
    "Budongo Forest": (1.82, 31.59, 0.15, "Tropical High Forest. Critical chimpanzee habitat."),
    "Bugoma Forest": (1.26, 30.97, 0.15, "Tropical High Forest. High community interface and edge-fire risk."),
    "Kabwoya Wildlife Reserve": (1.49, 31.10, 0.10, "Rift Escarpment. Steep terrain promoting rapid uphill fire spread."),
    "Kibale Forest (KCA)": (0.44, 30.37, 0.20, "Moist Evergreen Forest. Primate density; fires are rare but catastrophic.")
}

MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4, 
    "May": 5, "June": 6, "July": 7, "August": 8, 
    "September": 9, "October": 10, "November": 11, "December": 12
}

# --- 2. Resource Loading ---
@st.cache_resource
def load_xgb_model():
    model = xgb.XGBRegressor()
    model.load_model('fire_model_V1.ubj')
    return model

model = load_xgb_model()

# --- 3. NASA FIRMS Live Data Fetcher ---
@st.cache_data(ttl=3600)  # Refresh every hour
def fetch_nasa_fires(lat, lon, buffer):
    """Pulls live fire detections from NASA FIRMS VIIRS S-NPP."""
    west, south = lon - buffer, lat - buffer
    east, north = lon + buffer, lat + buffer
    
    # Using VIIRS S-NPP (SNPP) for higher 375m resolution
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{NASA_MAPKEY}/VIIRS_SNPP_NRT/{west},{south},{east},{north}/1"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return pd.read_csv(io.StringIO(response.text))
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- 4. Prediction & PDF Engines ---
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

def create_pdf(site, month, ndvi, risk, description):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(200, 10, txt="FireLens Uganda: Official Risk Report", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, txt="Albertine Rift Conservation Monitoring Unit", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt=f"Protected Area: {site}", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, txt=f"Forecast Window: {month} 2026", ln=True)
    pdf.cell(0, 8, txt=f"Baseline NDVI: {ndvi}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt=f"OFFICIAL ALERT STATUS: {risk} RISK", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Ecosystem Context:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, txt=description)
    return pdf.output()

# --- 5. Sidebar UI ---
st.sidebar.title("🛡️ FireLens Portal")
st.sidebar.markdown("Albertine Rift Wildfire Decision Support")
selected_name = st.sidebar.selectbox("Select Protected Area / AOI", list(SITES.keys()))
selected_month_name = st.sidebar.select_slider("Forecast Month", options=list(MONTH_MAP.keys()))
target_month = MONTH_MAP[selected_month_name]

ndvi_sim = st.sidebar.slider("Simulated NDVI (Vegetation Status)", 0.0, 1.0, 0.25)
st.sidebar.caption("💡 0.25 represents typical dry-season vegetation.")

st.sidebar.markdown("---")
st.sidebar.subheader("Live Satellite Layers")
show_nasa = st.sidebar.checkbox("Show NASA Live Fires (24h)", value=True)

# --- 6. Main Map Interface ---
st.header(f"Operational Dashboard: {selected_name}")
site_lat, site_lon, site_buffer, site_desc = SITES[selected_name]

with st.spinner("Analyzing model predictions and NASA live feeds..."):
    m = folium.Map(location=[site_lat, site_lon], zoom_start=11)
    
    # Google Hybrid Layer
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google', name='Satellite Labels', overlay=False, control=False
    ).add_to(m)

    # 1. Prediction Heatmap
    heat_data = get_aoi_predictions(model, site_lat, site_lon, site_buffer, ndvi_sim, target_month)
    if heat_data:
        HeatMap(heat_data, radius=75, blur=15, min_opacity=0.4).add_to(m)

    # 2. NASA Live Detections
    if show_nasa:
        live_fires = fetch_nasa_fires(site_lat, site_lon, site_buffer)
        if not live_fires.empty:
            for _, row in live_fires.iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=9, color='red', fill=True, fill_color='orange',
                    popup=f"NASA Detection: {row['acq_time']} UTC<br>Brightness: {row['bright_ti4']}K"
                ).add_to(m)
            st.sidebar.success(f"🔥 {len(live_fires)} active detections.")
        else:
            st.sidebar.info("No active fires detected (24h).")

    # 3. Boundaries
    folium.Rectangle(bounds=[[site_lat-site_buffer, site_lon-site_buffer], [site_lat+site_buffer, site_lon+site_buffer]],
                     color="darkgreen", weight=2, fill=False).add_to(m)
    
    st_folium(m, width="100%", height=600)

# --- 7. Summary & Reporting ---
st.markdown("---")
risk_level = "PEAK" if target_month in [1, 2, 12] else "REDUCED"

col1, col2 = st.columns(2)
with col1:
    st.info(f"**Site Profile:** {site_desc}")
    st.warning(f"**Seasonal Outlook:** {selected_month_name} is historically a **{risk_level}** risk period.")

with col2:
    st.write("### 📄 Reporting")
    pdf_output = create_pdf(selected_name, selected_month_name, ndvi_sim, risk_level, site_desc)
    st.download_button(label="Download Risk Report (PDF)", data=pdf_output, 
                       file_name=f"FireLens_{selected_name}.pdf", mime="application/pdf")

st.caption("Data: NASA FIRMS (Live) | XGBoost (Predictive) | Sentinel-2 (Baseline)")