# FireLens User Manual

**Version:** 1.0  
**Last Updated:** February 2026  
**Target Audience:** Command Center Operators, Park Wardens, and Incident Commanders.

---

## 📖 Introduction

**FireLens** is a tactical command and control dashboard designed effectively for Uganda's Protected Areas. It empowers park management to monitor wildfire risks in real-time, coordinate field responses, and analyze historical data.

The system fuses data from three powerful sources:
1.  **NASA VIIRS Satellites:** For detecting active fires (thermal anomalies) in real-time.
2.  **Sentinel-2 Imagery:** For analyzing vegetation health (fuel loads) and dryness (NDVI).
3.  **Field Rangers:** Ground truth reports via ODK mobile tools.

---

## 🚀 Getting Started

### 1. System Requirements
*   **Device:** Desktop or Laptop computer (Recommended for map visualization).
*   **Browser:** Google Chrome, Firefox, or Edge.
*   **Network:** Stable internet connection is required for live satellite data fetching.

### 2. Accessing the Portal
Navigate to the hosted URL provided by your IT administrator. Valid credentials may be required if authentication is enabled.

---

## 🖥️ Interface Overview

The interface is divided into two main zones:

### 1. The Tactical Sidebar (Left)
This is your **Control Panel**.
*   **Target Protected Area:** Select the specific Park or Reserve you want to monitor (e.g., *Murchison Falls NP*).
*   **Forecast Month:** Adjust this slider to the current month to calibrate the AI risk model.
*   **Upload Map Snapshot:** Optional feature to overlay static situation maps.
*   **System Status:** Indicators at the bottom show if the system is ONLINE and the last update time (EAT).

### 2. The Main Dashboard (Right)
This is your **Situation Room**. It automatically updates based on your Sidebar selections.
*   **Top Metrics Bar:** Provides an instant health check of the AOI.
    *   *Vegetation NDVI:* Greenness index (Lower numbers = Drier/Higher Risk).
    *   *Active Fires:* Count of currently burning fires detected by NASA.
    *   *AI Risk Score:* Probability of fire spread based on predictive modeling.
    *   *Status:* Overall Risk Alert Level (LOW, MODERATE, HIGH, CRITICAL).

---

## 🛠️ Operational Workflows

### 1. Monitoring & Situation Awareness
**Goal:** Assess the current fire threat level.
1.  Select your **Park** from the sidebar.
2.  Wait for the "Processing spatial intelligence..." spinner to complete.
3.  **Check the Risk Level:**
    *   🟢 **LOW/MODERATE:** Routine monitoring.
    *   🔴 **HIGH/CRITICAL:** Immediate attention required. Check the **Tactical Map**.

### 2. Using the Tactical Map 🗺️
**Tab:** `Tactical Map`
*   **Navigation:** Click and drag to pan; use `+`/`-` or scroll to zoom.
*   **Layers:**
    *   🔴 **Red Markers:** Live active fires detected by NASA VIIRS.
    *   🔥 **Heatmap Overlay:** Areas predicted to be at high risk by the AI model.
    *   📷 **Camera Icons (Green/Red):** Field reports submitted by rangers (Green = Safe/Controlled, Red = Active Threat).

### 3. Analyzing Vegetation & Weather 📊
**Tab:** `Analysis`
*   **Site Context:** Brief geographical overview of the selected AOI.
*   **Coordinates Table:** A raw list of active fire coordinates (`Latitude`, `Longitude`) that can be copied and sent to field teams.
*   **Visual Intelligence Gallery:**
    *   Displays the most recent **Sentinel-2 Satellite Image** of the area.
    *   **Metadata:** Check "Cloud Cover" to verify visibility.
    *   **Copernicus Browser:** Click the button to open a professional satellite analysis tool for deep-dive inspection.

### 4. Managing Field Reports (ODK) 🧾
**Tab:** `Field Reports`
*   **Review:** Scroll through photos and notes submitted by rangers on the ground.
*   **Action:** Click the **"📍 Locate on Map"** button below any report to instantly zoom the Tactical Map to that specific location.
*   **Severity:** Note the severity tag (e.g., `Extreme`, `Manageable`) to prioritize response.

### 5. Historical Analysis 📈
**Tab:** `History`
*   **Trend Chart:** View fire frequency over the last 6 months.
*   **Patterns:** Look for spikes in the chart to identify seasonal "slash and burn" cycles or recurring hotspots.
*   **Stats:** "Peak Activity Day" helps in planning future patrols.

### 6. Dispatching Alerts 📢
**Tab:** `Dispatch`
**⚠️ CAUTION:** This triggers real alarms to field personnel.
1.  Read the **Unified Command Broadcast** section.
2.  Click **"🚀 INITIATE MULTI-CHANNEL DISPATCH"**.
3.  **Monitor Progress:** A status box will show the system contacting SMS, WhatsApp, and Email gateways.
4.  **Verification:** Review the "Field Dispatch Status" list to see which rangers successfully received the alert.
5.  **Logs:** Use the "Operational Reports" section to download a CSV log of the dispatch for audit purposes.

### 7. Managing the Directory 📞
**Tab:** `Directory`
**Goal:** Ensure the right people get alerts.
*   **Edit:** You can directly type into the table to update phone numbers or emails.
*   **Assign AOI:** Change the "Primary AOI" dropdown for a ranger to move them to a different park assignment.
*   **Active Status:** Uncheck the "On Duty?" box to temporarily disable alerts for a ranger (e.g., if they are on leave).

---

## ❓ Troubleshooting

| Issue | Possible Cause | Solution |
| :--- | :--- | :--- |
| **"Cloud cover too high"** | Satellite view is obstructed. | Wait for the next satellite pass (approx. 2-5 days) or rely on thermal (NASA) data which sees through smoke/clouds. |
| **Map visual tiles not loading** | Internet connectivity. | Check your connection. The map relies on Google Satellite tiles. |
| **Dispatch fails** | Invalid contact info. | Check the `Directory` tab. Ensure phone numbers use the international format `+256...`. |
| **No Active Fires shown** | Satellite pass timing. | NASA satellites pass twice daily. A fire might have started *after* the last pass. Use ODK field reports for real-time verification. |

---

## 📞 Support
For technical issues, system errors, or to request a new Park/AOI addition:
*   **Technical Lead:** [Insert Name]
*   **IT Support Email:** [Insert Email]
