import xgboost as xgb
import pandas as pd
import numpy as np
import streamlit as st

# ---  Resource Loading ---
@st.cache_resource
def load_xgb_model(model_path='assets/fire_model_V1.ubj'):

    """
    Loads model once and keeps it in memory to prevent lag.
        across all sessions
    """
    try:
        model = xgb.XGBRegressor()
        model.load_model(model_path)
        return model
    except Exception as e:
        st.error(f"Failed to load model from {model_path}: {e}")
        return None


# ---  Cached Prediction ---
@st.cache_data
def get_aoi_predictions(_model, lat, lon, buffer, ndvi, month):
    """
    Caches results so switching sites or months is instant.

    Generates a 25x25 grid of risk predictions for the selected Area of Interest (AOI).
    
    Args:
        _model: The loaded XGBoost model instance.
        lat, lon: Center coordinates of the site.
        buffer: The degree radius to cover.
        ndvi: The satellite-derived greenness index.
        month: The numeric month (1-12) for seasonal weighting.
        
    Returns:
        List of [lat, lon, risk_score] for points exceeding the risk threshold.

    """

    # create a spatial within the site boundaries
    lats = np.linspace(lat - buffer, lat + buffer, 25)
    lons = np.linspace(lon - buffer, lon + buffer, 25)

    prediction_results = []

# Iterate through the grid to assess risk at each point
    for lt in lats:
        for ln in lons:
            # Prepare feature vector matching the model's training schema
            # Features: x (Lon), y (Lat), NDVI, MONTH, YEAR, CONFIDENCE_l, CONFIDENCE_n
            input_df = pd.DataFrame([[ln, lt, ndvi, month, 2026, 0, 1]],
                                     columns=['x', 'y', 'NDVI', 'MONTH', 'YEAR', 'CONFIDENCE_l', 'CONFIDENCE_n'])
            #perform inference  
            pred_score = float(_model.predict(input_df)[0])
            # Filter: Only record points where risk is significant (e.g., > 61%)
            if pred_score > 61:
                prediction_results.append([float(lt), float(ln), pred_score])
                
    return prediction_results