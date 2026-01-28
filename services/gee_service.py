import ee
import streamlit as st
import datetime

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

def mask_s2_clouds(image):
    """Internal helper to remove clouds from Sentinel-2 imagery using the QA60 band."""
    qa = image.select('QA60')
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    # Bits 10 and 11 are clouds and cirrus, respectively.
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
    return image.updateMask(mask).divide(10000)

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