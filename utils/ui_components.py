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

# Green blinking light to confirm connection GEE and NASA
st.markdown("""
    <style>
        /* Heartbeat Animation */
        @keyframes heartbeat {
            0% { opacity: 1; }
            50% { opacity: 0.3; }
            100% { opacity: 1; }
        }
        .heartbeat-icon {
            color: #00ff00;
            animation: heartbeat 1.5s ease-in-out infinite;
            font-size: 12px;
            margin-right: 5px;
        }
        .status-text {
            font-size: 12px;
            color: #808495;
            font-family: monospace;
        }
    </style>
""", unsafe_allow_html=True)

#for history tab
st.markdown("""
    <style>
        .stChart {
            background-color: #1a1c24;
            border-radius: 10px;
            padding: 10px;
            border: 1px solid #333;
        }
    </style>
""", unsafe_allow_html=True)

# for satellite snapshot image
st.markdown("""
    <style>
        .stImage > img {
            border-radius: 15px;
            border: 2px solid #1b3d2f;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            transition: transform 0.3s ease;
        }
        .stImage > img:hover {
            transform: scale(1.02);
            border-color: #ffcc80;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        /* Styling for the Metadata Box */
        .stMarkdown div[data-testid="stMarkdownContainer"] blockquote {
            background-color: #0d1a13;
            border-left: 5px solid #ffcc80;
            padding: 10px;
            border-radius: 5px;
        }
        /* Style for the link button to look more like a ranger tool */
        .stButton button {
            background-color: #1b3d2f !important;
            color: #ffcc80 !important;
            border: 1px solid #ffcc80 !important;
        }
    </style>
""", unsafe_allow_html=True)

