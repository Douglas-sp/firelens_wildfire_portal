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
   __Responsibility:__ Stores static data so we don't clutter the main logic.\
   __Content:__ The `SITES` dictionary (coordinates, descriptions), `MONTH_MAP`, and global settings like Page Layout config.

3. ##### *services/gee_service.py*
   __Responsibility:__ Talks to the satellite backend.\
   __Content:__ `initialize_gee()`, `mask_s2_clouds()`, and `get_live_ndvi()`. This isolates the complex Earth Engine authentication logic from the UI.

4. ##### *services/nasa_service.py*
   __Responsibility:__ Fetches live fire data.\
   __Content:__ `fetch_nasa_fires()`. If we add the alert system later, this file will also contain the logic to check if those fires are near sensitive areas.

5. `##### *services/model_service.py*`
   __Responsibility:__ Manages the AI.\
   __Content:__ `load_xgb_model()` and `get_aoi_predictions()`.

5. `##### *utils/pdf_generator.py*`
   __Responsibility:__ Generates the tactical report.\
   __Content:__ The large `create_pdf()` function.

7. ##### *app.py (The Main File)*
   __Responsibility:__ The Dashboard UI only.\
   __Content:__ Sidebar inputs, session state management, and assembling the visual blocks (Map, Table, Download Button) by calling the functions from the modules above.

