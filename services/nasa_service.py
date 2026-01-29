import pandas as pd
import requests
import io
import streamlit as st

@st.cache_data(ttl=3600) # Cache for 1 hour to respect API limits
def fetch_nasa_fires(lat, lon, buffer, api_key):
    """Fetches VIIRS SNPP fire data from NASA FIRMS within a bounding box."""
    west, south = lon - buffer, lat - buffer
    east, north = lon + buffer, lat + buffer
    
    # Requesting the last 24 hours of data in CSV format
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{api_key}/VIIRS_SNPP_NRT/{west},{south},{east},{north}/1"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            return df
        return pd.DataFrame()
    except Exception as e:
        st.warning(f"NASA FIRMS fetch failed: {e}")
        return pd.DataFrame()



def fetch_historical_fires(lat, lon, buffer, api_key, days_back=180):
    """
    Fetches historical fire data from NASA FIRMS for the last X days.
    """
    # VIIRS SNPP is reliable for historical trends
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{api_key}/VIIRS_SNPP_NRT/{lon-buffer},{lat-buffer},{lon+buffer},{lat+buffer}/{days_back}"
    
    try:
        df = pd.read_csv(url)
        if not df.empty:
            df['acq_date'] = pd.to_datetime(df['acq_date'])
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"History Fetch Error: {e}")
        return pd.DataFrame()