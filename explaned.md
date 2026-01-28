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
**Is it dry?** (NDVI < 0.24) ➡️ +1 Risk Point
**Does the AI see a pattern?** (AI > 75%) ➡️ +1 Risk Point
**Is something actually burning?** (NASA > 330K) ➡️ +1 Risk Point

**Result:** 2 points = **HIGH**, 3 points = **CRITICAL**. Both will now trigger an auto-alert.



