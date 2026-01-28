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

1. # *config.py* <br>
Responsibility: Stores static data so we don't clutter the main logic.
Content: The SITES dictionary (coordinates, descriptions), MONTH_MAP, and global settings like Page Layout config.

3. # *services/gee_service.py*\
Responsibility: Talks to the satellite backend.\
Content: initialize_gee(), mask_s2_clouds(), and get_live_ndvi(). This isolates the complex Earth Engine authentication logic from the UI.

3. # *services/nasa_service.py*\
   Responsibility: Fetches live fire data.\
Content: fetch_nasa_fires(). If we add the alert system later, this file will also contain the logic to check if those fires are near sensitive areas.

4. *services/model_service.py*\
__Responsibility:__ Manages the AI.\
Content: load_xgb_model() and get_aoi_predictions().

5. *utils/pdf_generator.py*\
**Responsibility:** Generates the tactical report.\
Content: The large create_pdf() function. Moving this out will save about 70 lines of code from your main app file.

6. *app.py (The Cleaned-Up Main File)*\
Responsibility: The Dashboard UI only.\
Content: Sidebar inputs, session state management, and assembling the visual blocks (Map, Table, Download Button) by calling the functions from the modules above.

