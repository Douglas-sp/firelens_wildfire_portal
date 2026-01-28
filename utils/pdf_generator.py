from fpdf import FPDF
import datetime
from PIL import Image
import os

def create_pdf(site, ndvi, risk, description, live_fires_df, map_image=None):
    """Generates a professional PDF report with a summary, map, and coordinate table."""
    pdf = FPDF()
    pdf.add_page()
    
    # --- Report Styling & Header ---
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(180, 0, 0) # Tactical Red
    pdf.cell(200, 15, txt="FireLens Uganda: Incident Report", ln=True, align='C')
    pdf.ln(5)
    
    # --- Tactical Summary Block ---
    num_total = len(live_fires_df)
    # Brightness temperature TI4 >= 330K is usually a high-intensity fire
    num_high = len(live_fires_df[live_fires_df['bright_ti4'] >= 330]) if num_total > 0 else 0
    eat_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    
    pdf.set_fill_color(240, 240, 240) # Light grey background
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, txt=f"  FIELD SUMMARY: {site}", ln=True, fill=True)
    
    pdf.set_font("Arial", size=10)
    pdf.cell(95, 8, txt=f"  Total Active Anomalies: {num_total}", border='LT')
    pdf.cell(95, 8, txt=f"  High Priority (Critical): {num_high}", border='RT', ln=True)
    pdf.cell(95, 8, txt=f"  Observation Time: {eat_time.strftime('%Y-%m-%d %H:%M')} EAT", border='LB')
    pdf.cell(95, 8, txt=f"  AOI Prediction Risk: {risk}", border='RB', ln=True)
    pdf.ln(8)

    # --- Site Context ---
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 6, txt=f"Area Context: {description}")
    pdf.ln(5)

    # --- Map Integration ---
    if map_image is not None:
        img = Image.open(map_image)
        temp_path = "temp_report_map.png"
        img.save(temp_path)
        pdf.image(temp_path, x=10, y=None, w=190)
        pdf.ln(5)
        if os.path.exists(temp_path): os.remove(temp_path)

    # --- Data Table ---
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Tactical GPS Coordinates", ln=True)
    
    if not live_fires_df.empty:
        pdf.set_font("Arial", 'B', 9)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(45, 7, "Latitude", 1, 0, 'C', True)
        pdf.cell(45, 7, "Longitude", 1, 0, 'C', True)
        pdf.cell(40, 7, "Intensity (K)", 1, 0, 'C', True)
        pdf.cell(50, 7, "Priority Status", 1, 1, 'C', True)
        
        pdf.set_font("Arial", size=9)
        for _, row in live_fires_df.iterrows():
            priority = "RED ALERT" if row['bright_ti4'] >= 330 else "Standard"
            pdf.cell(45, 7, str(round(row['latitude'], 5)), 1, 0, 'C')
            pdf.cell(45, 7, str(round(row['longitude'], 5)), 1, 0, 'C')
            pdf.cell(40, 7, str(row['bright_ti4']), 1, 0, 'C')
            pdf.cell(50, 7, priority, 1, 1, 'C')
    else:
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, txt="No active detections in the past 24 hours.", ln=True)
    
    return bytes(pdf.output())