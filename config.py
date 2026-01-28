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