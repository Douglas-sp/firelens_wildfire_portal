# firelens_wildfire_portal DIRECTORY_MAP 

```
firelens_uganda/
├── .streamlit/
│   └── secrets.toml          # API Keys (NASA, GEE)
├── assets/
│   └── fire_model_V1.ubj     # XGBoost Model File
├── services/                 # BUSINESS LOGIC ( The "Brain" )
│   ├── __init__.py
│   ├── gee_service.py        # Handles Google Earth Engine & NDVI
│   ├── nasa_service.py       # Handles NASA FIRMS API calls
│   └── model_service.py      # Handles XGBoost loading & prediction
├── utils/                    # HELPER FUNCTIONS ( The "Tools" )
│   ├── __init__.py
│   ├── pdf_generator.py      # PDF Report Logic
│   └── map_utils.py          # Folium map helpers
├── config.py                 # Constants (Site Lists, Month Maps)
└── app.py                    # MAIN ENTRY POINT ( The "Face" )
```
 ## Module Breakdown  
 Here is how we will distribute the current code:

1. ##### *config.py*
   __Responsibility:__ Stores static data for constants and site metadata.\
   __Content:__ The `SITES` dictionary (coordinates, descriptions), `MONTH_MAP`, and global settings like Page Layout config.

2. ##### *services/gee_service.py*
   __Responsibility:__ Talks to the satellite backend.\
   * Remote sensing. All logic involving Google Earth Engine (GEE)\
   __Content:__ `initialize_gee()`, `mask_s2_clouds()`, and `get_live_ndvi()`. This isolates the complex Earth Engine authentication logic from the UI.

3. ##### *services/nasa_service.py*
   __Responsibility:__ Fetches live fire data.\
   * Fetching near-real-time (NRT) thermal anomalies.\
   __Content:__ `fetch_nasa_fires()`. If we add the alert system later, this file will also contain the logic to check if those fires are near sensitive areas.

4. ##### *services/model_service.py*
   __Responsibility:__ Manages the AI.\
   * Loading the XGBoost model and making predictions.\
   __Content:__ `load_xgb_model()` and `get_aoi_predictions()`.

5. ##### *utils/pdf_generator.py*
   __Responsibility:__ Generates the tactical report.\
   * Formatting and exporting data into a tactical PDF.\
   __Content:__ The large `create_pdf()` function.

6. ##### *app.py (The Main File)*
   __Responsibility:__ The Dashboard UI only.\
   * Sidebar inputs, session state management, and assembling the visual blocks (Map, Table, Download Button) by calling the functions from the modules above.

# FireLens Wildfire Portal - System Explanation

## 1. High-Level Purpose
This is a **Wildfire Monitoring & Early Warning System** designed effectively for Uganda's protected areas (like Murchison Falls NP). It combines **live satellite data** (NASA & Google Earth Engine) with an **AI model** (XGBoost) to assess fire risk in real-time and dispatch alerts.

## 2. System Workflow (The "Story")
The system follows a linear pipeline: **Input → Ingestion → Processing → Action**.

### Step 1: User Selection (Inputs)
*   **File:** `app.py`, `config.py`
*   **Action:** The user selects a **Protected Area** (e.g., "Murchison Falls NP") and a **Forecast Month** from the sidebar.
*   **Detail:** The app loads static coordinates and metadata for the site from `config.py`.

### Step 2: Data Ingestion (Live Satellite Data)
The system pulls real-time environmental data from two key external sources:
1.  **Vegetation Dryness (Fuel Load):**
    *   **File:** `services/gee_service.py`
    *   **Action:** Connects to **Google Earth Engine (GEE)**.
    *   **Logic:** It fetches Sentinel-2 satellite imagery, removes clouds (`mask_s2_clouds`), and calculates the **NDVI** (Normalized Difference Vegetation Index) for the last 60 days. This tells the system how dry or compliant the vegetation is (Fuel State).
2.  **Active Fires (Ignition):**
    *   **File:** `services/nasa_service.py`
    *   **Action:** Connects to **NASA FIRMS API**.
    *   **Logic:** It asks NASA for all thermal anomalies (fires) detected by the VIIRS satellite within the site's bounding box over the last 24 hours.

### Step 3: The "Brain" (Risk Assessment)
Once data is fetched, the system assesses the danger level.
1.  **AI Prediction (Pattern Matching):**
    *   **File:** `services/model_service.py`
    *   **Action:** Loads a pre-trained **XGBoost Model** (`assets/fire_model_V1.ubj`).
    *   **Logic:** It generates a grid of points across the park and predicts the likelihood of fire for *each point* based on the current Month, Location, and Live NDVI.
2.  **Risk Logic (Decision Making):**
    *   **File:** `services/alert_service.py`
    *   **Action:** `evaluate_risk_level()` combines all factors.
    *   **Rules:**
        *   **CRITICAL:** If Vegetation is extremely dry (NDVI < 0.22) OR massive fires are already burning.
        *   **HIGH:** If the AI Model predicts > 80% probability of fire.
        *   **Alerts:** It generates specific warning messages (e.g., "🚩 CRITICAL FUEL").

### Step 4: User Outputs (Visualization & Action)
Finally, the system presents the data and acts on it.
1.  **Dashboard:** (`app.py`) shows a **Folium map** with the site boundaries and red markers for any active fires.
2.  **Reporting:** (`utils/pdf_generator.py`) generates a downloadable **PDF Tactical Report** summarizing the risk and listing specific fire coordinates for rangers.
3.  **Notifications:** (`services/notification_service.py`)
    *   **Action:** If the Risk is **CRITICAL** and `AUTO_ALERT_ENABLED` is True, it automatically sends a **Telegram message** to the ranger team with the status and location details.

## Summary of Files
*   **`app.py`**: The "Face". Handles UI and orchestrates the flow.
*   **`config.py`**: The "Settings". Stores site coordinates and thresholds.
*   **`services/gee_service.py`**: The "Sensor". Talks to satellites for vegetation data.
*   **`services/nasa_service.py`**: The "Watchtower". Checks for active fires.
*   **`services/model_service.py`**: The "Oracle". Uses AI to predict future risk.
*   **`services/alert_service.py`**: The "Judge". Decides if a situation is dangerous.
*   **`services/notification_service.py`**: The "Messenger". Sends Telegram alerts.
*   **`utils/pdf_generator.py`**: The "Scribe". Writes the PDF report.

## Summary of Logic Flow
*  **Is it dry?** (NDVI < 0.24) ➡️ +1 Risk Point
*  **Does the AI see a pattern?** (AI > 75%) ➡️ +1 Risk Point
*  **Is something actually burning?** (NASA > 330K) ➡️ +1 Risk Point

* **Result:** 2 points = **HIGH**, 3 points = **CRITICAL**. Both will now trigger an auto-alert.



