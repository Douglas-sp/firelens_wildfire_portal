import streamlit as st

def inject_custom_css():
    """
    Injects professional, dark-mode CSS with custom animations 
    for the FireLens Command Center.
    """
    st.markdown("""
        <style>
            /* 1. Global Tactical Theme */
            .stApp {
                background-color: #0e1117;
                color: #e0e0e0;
            }
            
            /* 2. Pulsing Animation Keyframes */
            @keyframes pulse-red {
                0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.7); }
                70% { box-shadow: 0 0 0 15px rgba(255, 75, 75, 0); }
                100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }
            }
            
            @keyframes pulse-orange {
                0% { box-shadow: 0 0 0 0 rgba(255, 170, 0, 0.7); }
                70% { box-shadow: 0 0 0 15px rgba(255, 170, 0, 0); }
                100% { box-shadow: 0 0 0 0 rgba(255, 170, 0, 0); }
            }

            /* 3. Banner Base Styling */
            .risk-banner {
                padding: 25px;
                border-radius: 12px;
                margin-bottom: 20px;
                text-align: center;
                transition: transform 0.3s ease;
            }

            /* 4. Level-Specific Styles */
            .risk-critical {
                background: linear-gradient(90deg, #440000, #660000);
                border: 2px solid #ff4b4b;
                animation: pulse-red 2s infinite;
            }

            .risk-high {
                background: linear-gradient(90deg, #442200, #663300);
                border: 2px solid #ffaa00;
                animation: pulse-orange 2s infinite;
            }

            .risk-normal {
                background: linear-gradient(90deg, #002200, #004400);
                border: 2px solid #00ff00;
                opacity: 0.9;
            }

            /* 5. Clean Metric Headers */
            [data-testid="stMetricLabel"] {
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: #808495;
            }
        </style>
    """, unsafe_allow_html=True)

def display_risk_banner(level, messages):
    """
    Renders the pulsing banner in the main UI based on the 
    risk score provided by the alert_service.
    """
    # Map level to CSS class
    bg_class = f"risk-{level.lower()}"
    
    # Determine Icon and Title
    if level == "CRITICAL":
        icon, title = "🚨", "CRITICAL THREAT DETECTED"
    elif level == "HIGH":
        icon, title = "⚠️", "HIGH RISK ADVISORY"
    else:
        icon, title = "✅", "SITUATIONAL STATUS: NORMAL"

    # Construct Message String
    msg_html = "".join([f"<div style='margin-top:5px;'>• {m}</div>" for m in messages]) if messages else "No anomalies detected."

    # Render HTML
    st.markdown(f"""
        <div class="risk-banner {bg_class}">
            <h2 style='margin:0; font-family:sans-serif; letter-spacing:2px;'>{icon} {title}</h2>
            <div style='font-size: 1.1rem; margin-top:10px; opacity:0.9;'>
                {msg_html}
            </div>
        </div>
    """, unsafe_allow_html=True)
    