import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import datetime
import os

# --- 1. INTERNAL MODULE IMPORTS ---
from config import SITES, MONTH_MAP, CURRENT_YEAR, AUTO_ALERT_ENABLED
from services.gee_service import get_live_ndvi, get_satellite_snapshot
from services.nasa_service import fetch_nasa_fires, fetch_historical_fires
from services.model_service import load_xgb_model, get_aoi_predictions
from services.alert_service import evaluate_risk_level
from services.notification_service import broadcast_to_directory
from services.odk_service import fetch_kobo_reports, fetch_kobo_image_bytes
from utils.pdf_generator import create_pdf
from utils.ui_components import inject_custom_css, display_risk_banner
from utils.contact_manager import load_contacts

# --- 2. SETUP & INITIALIZATION ---
st.set_page_config(
    page_title="FireLens Uganda | Tactical Command",
    page_icon="🔥",
    layout="wide"
)

inject_custom_css()
NASA_KEY = st.secrets['NASA_MAPKEY']
model = load_xgb_model()

# --- 3. SIDEBAR UI (Input & Configuration) ---
with st.sidebar:
    st.title("FireLens Portal")
    st.subheader("Tactical Configuration")
    
    # Selection determines the site
    selected_site = st.selectbox("Target Protected Area", list(SITES.keys()))
    
    # IMMEDIATELY DEFINE lat/lon so they are available for the rest of the script
    lat, lon, buffer, desc = SITES[selected_site]

    # RESET LOGIC: If site changes, update the map center
    if 'last_site' not in st.session_state or st.session_state['last_site'] != selected_site:
        st.session_state['map_center'] = [lat, lon]
        st.session_state['map_zoom'] = 11 
        st.session_state['last_site'] = selected_site
    
    # Initialize session states if not present
    if 'map_center' not in st.session_state:
        st.session_state['map_center'] = [lat, lon]
    if 'map_zoom' not in st.session_state:
        st.session_state['map_zoom'] = 11

    # Function to change map view (used by ODK "Locate" buttons)
    def fly_to_site(target_lat, target_lon):
        st.session_state['map_center'] = [target_lat, target_lon]
        st.session_state['map_zoom'] = 15 

    st.divider()
    target_month_name = st.select_slider("Forecast Month", options=list(MONTH_MAP.keys()))
    target_month = MONTH_MAP[target_month_name]
    
    # map_snapshot = st.file_uploader("Upload Map Snapshot", type=['png', 'jpg'])

    # Sidebar Footer
    st.divider()
    st.markdown("""
        <div style='display: flex; align-items: center; justify-content: center;'>
            <span class='heartbeat-icon'>●</span>
            <span class='status-text'>SYSTEM LIVE</span>
        </div>
    """, unsafe_allow_html=True)
    st.caption(f"Update: {datetime.datetime.now().strftime('%H:%M:%S')} EAT")

# --- 4. DATA SYNCHRONIZATION ---
if 'ndvi' not in st.session_state or st.session_state.get('last_site_ndvi') != selected_site:
    with st.spinner("🛰️ Syncing Satellite Fuel Data..."):
        st.session_state['ndvi'] = get_live_ndvi(lat, lon, buffer)
        st.session_state['last_site_ndvi'] = selected_site

with st.spinner("Processing spatial intelligence..."):
    heat_data = get_aoi_predictions(model, lat, lon, buffer, st.session_state['ndvi'], target_month)
    live_fires = fetch_nasa_fires(lat, lon, buffer, NASA_KEY)

risk_level, alert_msgs, is_dispatch_worthy = evaluate_risk_level(st.session_state['ndvi'], heat_data, live_fires)

# --- 5. TOP-LEVEL DASHBOARD ---
st.title(f"{selected_site}")
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("Vegetation NDVI", st.session_state['ndvi'])
m_col2.metric("Active Fires", len(live_fires))
m_col3.metric("AI Risk Score", f"{round(max([p[2] for p in heat_data]), 1) if heat_data else 0}%")
m_col4.metric("Status", risk_level)

# --- 6. TACTICAL TABS ---
tab_map, tab_analytics, tab_odk, tab_history, tab_dispatch, tab_directory, tab_help = st.tabs([
    "Tactical Map", "Analysis", "Field Reports", "History", "Dispatch", "Directory", "Help"
])

with tab_map:
    display_risk_banner(risk_level, alert_msgs)
    
    # 1. Initialize Folium Map
    m = folium.Map(location=st.session_state['map_center'], zoom_start=st.session_state['map_zoom'], tiles=None)
    folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google', name='Satellite').add_to(m)

    # 2. Add Heatmap
    # Filter out low-probability points to reduce noise - allowing only points with probability > 0.65
    # heat_data = [point for point in heat_data if point[2] > 0.65]
    if heat_data:
        HeatMap(
            heat_data,
            radius=5, #size of the heatmap - larger radius = larger heatmap and makes it look like a zone
            blur=35, #blur of the heatmap - larger blur = larger heatmap
            min_opacity=0.4, #opacity of the heatmap - lower opacity = more transparent
            gradient={0.4: 'blue', 0.67: 'yellow', 0.9: 'red'} #colors of the heatmap - 
        ).add_to(m)

    # 3. Add NASA Markers
    if not live_fires.empty:
        for _, row in live_fires.iterrows():
            folium.CircleMarker([row['latitude'], row['longitude']], radius=10, color='#ff4b4b', fill=True).add_to(m)

    # 4. Add ODK Ground Reports (Crucial: Add to 'm' before rendering)
    ground_reports = fetch_kobo_reports()
    if not ground_reports.empty:
        for _, report in ground_reports.iterrows():
            color = 'red' if report['incident_type'] == 'real_fire' else 'green'
            folium.Marker(
                location=[report['lat'], report['lon']],
                popup=f"ODK: {report['fire_severity']} severity",
                icon=folium.Icon(color=color, icon='camera')
            ).add_to(m)

    # 5. Render Map
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
            "Export Tactical PDF Report", 
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

    st.divider()
    st.subheader("Visual Intelligence Gallery")

    # Fetch URL and Metadata
    snapshot_url, acq_date, clouds = get_satellite_snapshot(lat, lon, buffer)

    if snapshot_url:
        g_col1, g_col2 = st.columns([1.5, 1])
    
        with g_col1:
            st.image(snapshot_url, caption=f"Sentinel-2 View: {selected_site}", use_container_width=True)
        
        with g_col2:
            st.markdown(f"""
            ### Image Metadata
            - **Acquisition Date:** `{acq_date}`
            - **Cloud Cover:** `{clouds}%`
            - **Sensor:** `Sentinel-2 (Optical)`
            
            **Intelligence Observations:**
            1. **Fuel Curing:** Check for yellowing patches indicating high-risk dry grass.
            2. **Access Roads:** Verify if fire-access tracks are clear and visible.
            3. **Burn Scars:** Look for black/dark-grey zones indicating recent fire activity.
        """)
        
        # Add a quick link to the official Copernicus Browser for deep diving
        st.link_button("🌐 Open Copernicus Browser", 
                       f"https://apps.sentinel-hub.com/eo-browser/?lat={lat}&lng={lon}&zoom=11")
    else:
        st.warning("⚠️ Cloud cover is currently too high to generate a clear visual snapshot.")


with tab_odk:
    st.subheader("Field Intelligence Gallery")
    if not ground_reports.empty:
        photo_reports = ground_reports.dropna(subset=['_attachments'])
        for i, (_, report) in enumerate(photo_reports.iterrows()):
            with st.container(border=True):
                col_img, col_info = st.columns([1, 1.5])
                
                # Fetch image bytes for this specific report
                attachments = report.get('_attachments', [])
                img_bytes = None
                if attachments:
                    img_bytes = fetch_kobo_image_bytes(attachments[0].get('download_url'))

                with col_img:
                    if img_bytes:
                        st.image(img_bytes, use_container_width=True)
                    else:
                        st.info("No photo provided")
                
                with col_info:
                    st.markdown(f"**Type:** {report['incident_type']} | **Severity:** `{report['fire_severity']}`")
                    st.button("📍 Locate on Map", key=f"btn_{i}", on_click=fly_to_site, args=(report['lat'], report['lon']), type="primary")
                    st.write(f"*Submitted: {report['_submission_time'][:16]}*")
                    with st.expander("Notes"):
                        st.write(report.get('notes', 'No notes.'))
    else:
        st.info("No ground reports found.")


with tab_history:
    st.subheader(f"Historical Fire Activity: {selected_site}")
    
    with st.spinner("Retrieving historical records..."):
        # Fetch data for the last 6 months
        hist_df = fetch_historical_fires(lat, lon, buffer, NASA_KEY)
        
        if not hist_df.empty:
            # Group by date to see frequency
            daily_counts = hist_df.groupby('acq_date').size().reset_index(name='Fire Count')
            
            # 1. Trend Chart
            st.line_chart(daily_counts, x='acq_date', y='Fire Count', color="#ff4b4b")
            
            # 2. Insights Column
            c1, c2 = st.columns(2)
            with c1:
                total_incidents = len(hist_df)
                st.metric("Total Detections (6mo)", total_incidents)
            with c2:
                peak_day = daily_counts.loc[daily_counts['Fire Count'].idxmax()]
                st.metric("Peak Activity Day", peak_day['acq_date'].strftime('%b %d'))
                
            st.caption("This data shows seasonal recurrence. High spikes often correlate with 'slash and burn' cycles near park boundaries.")
        else:
            st.info("No significant fire history recorded in this area for the last 180 days.")

with tab_dispatch:
    st.subheader("Unified Command Broadcast")
    st.write("Triggering this will alert all field rangers via SMS, Email, and Telegram.")

    if st.button("INITIATE MULTI-CHANNEL DISPATCH", use_container_width=True):
        with st.status("Dispatching alerts across Uganda...", expanded=True) as status:
            st.write("Checking Satellite bridge...")
            # Run the broadcast
            dispatch_report = broadcast_to_directory(selected_site, risk_level, alert_msgs)
            
            if dispatch_report:
                st.write("### Field Dispatch Status")
                for entry in dispatch_report:
                    st.write(f"**{entry['Name']}**: {entry['Status']}")
            else:
                st.warning("No active personnel found for this Area of Interest.")
            
            status.update(label="Broadcast Complete", state="complete", expanded=False)
        
        st.balloons() # Visual confirmation for the user -Just for fun 😁

# Operational Reports/ Monthly dispatch report
    st.divider()
    st.subheader("Operational Reports")
    st.write("Download monthly dispatch logs for official reporting.")
    
    if os.path.exists("logs"):
        log_files = [f for f in os.listdir("logs") if f.endswith(".csv")]
        selected_log = st.selectbox("Select Month", sorted(log_files, reverse=True))
        
        if selected_log:
            log_path = os.path.join("logs", selected_log)
            df_log = pd.read_csv(log_path)
            
            # Preview the last 5 dispatches
            st.dataframe(df_log.tail(5), use_container_width=True)
            
            # Download Button
            with open(log_path, "rb") as f:
                st.download_button(
                    label=f"Download {selected_log}",
                    data=f,
                    file_name=selected_log,
                    mime="text/csv"
                )
    else:
        st.info("No logs generated yet. Logs will appear after your first dispatch.")

with tab_directory:
    
    st.subheader(" Field Personnel & AOI Assignment")

    contacts_df = load_contacts()

    # Defining the list of valid parks for the dropdown from "SITES" DICTIONARY and adding "ALL"
    park_list = list(SITES.keys())
    if "ALL" not in park_list:
        park_list.append("ALL")

    edited_df = st.data_editor(
        contacts_df,
        column_config={
            "Assigned_Sites": st.column_config.SelectboxColumn(
                "Primary AOI",
                help="Which Protected Area (park/Forest/Reserve) is this ranger assigned to?",
                options=park_list,
                required=True,
            ),
            "Active": st.column_config.CheckboxColumn("On Duty?"),
            "Email": st.column_config.TextColumn(
                "Email Address",
                validate="^[^@]+@[^@]+\.[^@]+$",
            ),
            "SMS_Phone": st.column_config.TextColumn(
                "Phone Number (SMS)",
                help="use international format: +256...",
                validate="^\+256\d{9}$",
            ),
        },
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
    )

    # if st.button("Sync Directory & AOIs"):
    #     save_contacts(edited_df)
    #     st.success("AOI Assignments Saved.")

with tab_help:
    st.subheader("FireLens Documentation Center")
    h_col1, h_col2 = st.columns([2, 1])

    with h_col1:
        st.markdown("### User Manual")
        try:
            with open("USER_MANUAL.md", "r", encoding="utf-8") as f:
                manual_content = f.read()
            # Render markdown in a scrollable container if possible, or just standard
            with st.container(height=600):
                st.markdown(manual_content, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Could not load User Manual: {e}")

    with h_col2:
        st.markdown("### Technical Resources")
        
        # Download User Manual
        if 'manual_content' in locals():
            st.download_button(
                label="Download User Manual (.MD)",
                data=manual_content,
                file_name="FireLens_User_Manual.md",
                mime="text/markdown",
                use_container_width=True
            )

        st.divider()

        # Technical Docs (explaned.md)
        try:
            with open("explaned.md", "r", encoding="utf-8") as f:
                tech_content = f.read()
            
            with st.expander("View System Architecture"):
                st.markdown(tech_content)
                
            st.download_button(
                label="Download Tech Specs (MD)",
                data=tech_content,
                file_name="FireLens_System_Architecture.md",
                mime="text/markdown",
                use_container_width=True
            )
        except Exception as e:
            st.warning("Technical documentation not found.")
            
        st.success("✅ **Support Contact**\n\nTechnical Lead: Raymond\n\nEmail: wamaniray@gmail.com")
