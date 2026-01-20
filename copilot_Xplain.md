GitHub Copilot

This code sets up the top portion of a Streamlit app for a wildfire‑risk portal. st.set_page_config configures the browser tab title to "Wildfire Risk Portal" and uses the "wide" layout so the app can use the full horizontal space of the page (useful for maps, plots, or wide forms).

It instantiates an XGBoost regressor and immediately loads a pre‑trained model file named 'fire_model_V1.ubj'. That file must exist at runtime and be compatible with the xgboost version used; otherwise load_model will raise an error. The comment reminds you that the filename must match whatever name you used when saving the model.

The next lines build a simple sidebar UI for stakeholder inputs. st.sidebar.header and st.sidebar.markdown add explanatory text, then a subheader and two sliders collect a latitude (lat) and longitude (lon) within bounds determined by the training data. The sliders use float values with a 0.01 step and sensible defaults.

Finally, the code adds a number_input for the target year with a limited range (2015–2030) and a default of 2026. This keeps inputs constrained to plausible simulation years.

