import ee
import streamlit as st
from datetime import datetime

# Initialize GEE Connection
def initialize_gee():
    """Authenticates and initializes the GEE connection using Streamlit secrets."""
    try:
        # Check if already initialized to avoid redundant calls
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

# Cloud Masking Function
def mask_s2_clouds(image):
    """Internal helper to remove clouds from Sentinel-2 imagery using the QA60 band."""
    qa = image.select('QA60')
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    # Bits 10 and 11 are clouds and cirrus, respectively.
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
    return image.updateMask(mask).divide(10000)

# NDVI Calculation Function
def get_live_ndvi(lat, lon, buffer_deg):
    """Calculates the median NDVI for a buffered point over the last 60 days."""
    initialize_gee()
    # Convert degrees to roughly meters for the buffer
    point = ee.Geometry.Point([lon, lat]).buffer(buffer_deg * 111000)
    
    # Set date range (60 days back from 'now' in GMT+3)
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    start_date = (now - datetime.timedelta(days=60)).strftime('%Y-%m-%d')
    
    collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                  .filterBounds(point)
                  .filterDate(start_date, now.strftime('%Y-%m-%d'))
                  .map(mask_s2_clouds))
    
    # Create a median composite and calculate NDVI
    composite = collection.median()
    ndvi = composite.normalizedDifference(['B8', 'B4']).rename('NDVI')
    
    # Reduce to a single mean value for the area
    stats = ndvi.reduceRegion(reducer=ee.Reducer.mean(), geometry=point, scale=30, maxPixels=1e9)
    res = stats.get('NDVI').getInfo()
    
    return round(res, 3) if res is not None else 0.25


# Satellite Snapshot Function
def get_satellite_snapshot(lat, lon, buffer):
    """
    Generates a True Color snapshot URL and retrieves the acquisition date.
    """
    try:
        aoi = ee.Geometry.Point([lon, lat]).buffer(buffer * 100000).bounds()
        
        # Fetch latest Sentinel-2 Image with low cloud cover
        image = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                 .filterBounds(aoi)
                 .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 15))
                 .sort('system:time_start', False)
                 .first())

        # Extract Date
        date_ms = image.get('system:time_start').getInfo()
        acquisition_date = datetime.fromtimestamp(date_ms/1000.0).strftime('%Y-%m-%d')
        cloud_score = round(image.get('CLOUDY_PIXEL_PERCENTAGE').getInfo(), 1)

        # Visualization Parameters
        vis_params = {
            'bands': ['B4', 'B3', 'B2'],
            'min': 0, 'max': 3000, 'gamma': 1.4,
            'dimensions': 800, 'format': 'jpg'
        }
        
        return image.getThumbURL(vis_params), acquisition_date, cloud_score
    except Exception as e:
        print(f"GEE Gallery Error: {e}")
        return None, None, None