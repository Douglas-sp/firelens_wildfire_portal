import streamlit as st

def inject_custom_css():
    """Injects custom CSS to give FireLens a dark, tactical dashboard feel."""
    st.markdown("""
        <style>
            /* Main Background and Text */
            .stApp {
                background-color: #0e1117;
                color: #e0e0e0;
            }
            
            /* Metric Card Styling */
            [data-testid="stMetricValue"] {
                font-size: 2rem;
                color: #ff4b4b;
            }
            
            /* Sidebar Styling */
            section[data-testid="stSidebar"] {
                background-color: #1a1c24;
                border-right: 1px solid #333;
            }

            /* Custom Banner for Risk Levels */
            .risk-banner {
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 25px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.1);
            }
            .risk-critical { background-color: #440000; border-left: 10px solid #ff0000; }
            .risk-high { background-color: #442200; border-left: 10px solid #ffaa00; }
            .risk-normal { background-color: #002200; border-left: 10px solid #00ff00; }
        </style>
    """, unsafe_allow_html=True)

def display_risk_banner(level, messages):
    """Displays a pulsing, colored banner based on the current risk level."""
    bg_class = f"risk-{level.lower()}"
    emoji = "🚨" if level == "CRITICAL" else "⚠️" if level == "HIGH" else "✅"
    
    st.markdown(f"""
        <div class="risk-banner {bg_class}">
            <h2 style='margin:0;'>{emoji} {level} RISK LEVEL</h2>
            <p style='margin:5px 0 0 0;'>{", ".join(messages) if messages else "All systems within normal parameters."}</p>
        </div>
    """, unsafe_allow_html=True)
    