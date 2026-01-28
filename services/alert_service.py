import pandas as pd
from config import THRESHOLD_NDVI_CRITICAL, THRESHOLD_PREDICTION_RISK, AUTO_DISPATCH_LEVELS

def evaluate_risk_level(ndvi, predictions, live_fires_df):
    """
    Analyzes data and determines if the situation warrants an automatic alert.
    Returns: (level_string, alert_messages, is_dispatch_worthy)
    """
    alerts = []
    risk_score = 0 # 0: Low, 1: Elevated, 2: High, 3: Critical
    
    # 1. Check Fuel State (NDVI)
    if ndvi <= THRESHOLD_NDVI_CRITICAL:
        alerts.append(f"🚩 CRITICAL FUEL: NDVI is {ndvi}. Vegetation is extremely dry.")
        risk_score += 1
        
    # 2. Check AI Forecast
    if predictions:
        max_pred = max([p[2] for p in predictions])
        if max_pred >= THRESHOLD_PREDICTION_RISK:
            alerts.append(f"🔮 AI FORECAST: High likelihood detected ({round(max_pred,1)}% match to fire patterns).")
            risk_score += 1
            
    # 3. Check Live Thermal Activity
    # 3. Check Live Thermal Activity
    if not live_fires_df.empty:
        high_intensity_count = len(live_fires_df[live_fires_df['bright_ti4'] >= 330])
        if high_intensity_count > 0:
            alerts.append(f"🔥 ACTIVE FIRE: {high_intensity_count} High-intensity thermal anomalies detected.")
            risk_score += 1

    # Mapping score to Level
    mapping = {
        0: "NORMAL", 
        1: "ELEVATED", 
        2: "HIGH", 3: "CRITICAL"
    }
    level = mapping.get(risk_score, "CRITICAL")
    
    # Check if this level triggers the automatic dispatch
    is_dispatch_worthy = level in AUTO_DISPATCH_LEVELS
    
    return level, alerts, is_dispatch_worthy