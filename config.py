import datetime

# --- Protected Area Metadata ---
# Format: "Name": (Lat, Lon, Buffer_Deg, Description)
SITES = {
    "Murchison Falls NP": (2.25, 31.79, 0.35, "Savanna/Woodland mosaic. High fuel load."),
    "Budongo Forest": (1.82, 31.59, 0.15, "Tropical High Forest. Primate habitat."),
    "Bugoma Forest": (1.26, 30.97, 0.15, "Tropical High Forest. Community edge risk."),
    "Kabwoya Wildlife Reserve": (1.49, 31.10, 0.10, "Rift Escarpment. Steep terrain."),
    "Kibale Forest (KCA)": (0.44, 30.37, 0.20, "Moist Evergreen. Primate density.")
}

# --- Temporal Mapping ---
MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
}

# --- Timezone Settings ---
UGANDA_TZ_OFFSET = 3  # GMT+3 (East Africa Time)
CURRENT_YEAR = 2026

# --- Alert Thresholds ---
THRESHOLD_NDVI_CRITICAL = 0.22  # Below this, vegetation is dangerously dry
THRESHOLD_PREDICTION_RISK = 80.0 # XGBoost confidence percentage
THRESHOLD_BRIGHTNESS_K = 330    # NASA VIIRS Brightness temperature for "High Intensity"

# --- Automation Settings ---
AUTO_ALERT_ENABLED = True  # Master toggle for automatic dispatch
# Define which levels qualify for automatic broadcast
AUTO_DISPATCH_LEVELS = ["CRITICAL"]

# --- Notification Settings ---
# These would typically come from st.secrets in a production environment
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"



