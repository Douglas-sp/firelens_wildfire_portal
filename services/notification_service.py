import requests
import streamlit as st

def send_telegram_alert(site_name, level, messages):
    """Sends a formatted emergency alert to a Telegram Chat/Group."""
    token = st.secrets.get("TELEGRAM_BOT_TOKEN")
    chat_id = st.secrets.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        return False, "Telegram credentials missing in secrets."

    header = f"🚨 *FIRELENS ALERT: {site_name}* 🚨\n"
    status = f"STATUS: *{level}*\n\n"
    body = "\n".join(messages)
    footer = "\n\n📍 _Check dashboard for navigation links._"
    
    full_message = header + status + body + footer
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": full_message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, data=payload)
        return response.status_code == 200, response.text
    except Exception as e:
        return False, str(e)