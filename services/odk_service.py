import requests
import pandas as pd
import streamlit as st


def fetch_kobo_reports():
    """
    Connects to KoboToolbox API and retrieves ground-truth reports.
    """
    # if "KOBO_API_TOKEN" not in st.secrets or "KOBO_ASSET_ID" not in st.secrets:
    #     st.warning("⚠️ KoboToolbox credentials not found in secrets.toml")
    #     return pd.DataFrame()
    token = st.secrets["KOBO_API_TOKEN"]
    asset_id = st.secrets["KOBO_ASSET_ID"] # The unique ID for your fire form
    url = f"https://kf.kobotoolbox.org/api/v2/assets/{asset_id}/data.json"
    
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                return pd.DataFrame()
            
            # Flatten the JSON into a DataFrame
            df = pd.DataFrame(results)
            
            # Extract Lat/Lon from the Kobo 'location' string
            if 'location' in df.columns:
                df[['lat', 'lon', 'alt', 'prec']] = df['location'].str.split(' ', expand=True).astype(float)
            
            return df
        else:
            st.error(f"Kobo API Error: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to sync ODK data: {e}")
        return pd.DataFrame()

# Get the media URL for Kobo
def get_kobo_media_url(file_path):
    """
    Constructs the authenticated URL for Kobo media attachments.
    """
    if pd.isna(file_path):
        return None
    
    # Standard Kobo media URL format
    # Replace 'kf.kobotoolbox.org' when using the 'kobo.humanitarianresponse.info' server
    base_url = "https://kf.kobotoolbox.org/api/v2/assets/{}/data/".format(st.secrets["KOBO_ASSET_ID"])
    
    # The API requires the token to view private media
    # Usually, for Streamlit 'st.image', we might need to download the byte content
    return file_path

# Download image from Kobo to display in the UI
@st.cache_data(ttl=600)  # Cache images for 10 minutes
def fetch_kobo_image_bytes(image_url):
    """
    Downloads image from Kobo using the secure API token.
    """
    headers = {"Authorization": f"Token {st.secrets['KOBO_API_TOKEN']}"}
    try:
        response = requests.get(image_url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None