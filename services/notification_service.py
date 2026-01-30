import streamlit as st
import smtplib
from email.message import EmailMessage
from twilio.rest import Client
import requests

# Telegram alert
def send_telegram_alert(site, level, messages):
    """Existing Telegram Logic."""
    token = st.secrets["TELEGRAM_BOT_TOKEN"]
    chat_id = st.secrets["TELEGRAM_CHAT_ID"]
    text = f"🚨 *{level} FIRE RISK: {site}*\n" + "\n".join([f"• {m}" for m in messages])
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}&parse_mode=Markdown"
    try:
        res = requests.get(url)
        return res.status_code == 200, "Sent"
    except Exception as e:
        return False, str(e)

# Email alert
def send_email_alert(site, level, messages):
    """Sends a formal email alert via SMTP."""
    msg = EmailMessage()
    msg.set_content(f"FireLens Alert for {site}\nRisk Level: {level}\n\nDetails:\n" + "\n".join(messages))
    msg['Subject'] = f"🔥 {level} Fire Risk Alert - {site}"
    msg['From'] = st.secrets["EMAIL_SENDER"]
    msg['To'] = "ranger_ops@uwa.go.ug" # Example recipient list

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(st.secrets["EMAIL_SENDER"], st.secrets["EMAIL_PASSWORD"])
            smtp.send_message(msg)
        return True
    except:
        return False

# SMS alert
def send_sms_alert(site, level, messages):
    """Sends a high-priority SMS (Twilio Example)."""
    try:
        client = Client(st.secrets["TWILIO_ACCOUNT_SID"], st.secrets["TWILIO_AUTH_TOKEN"])
        body = f"FireLens {level}: {site}. Check portal for coords."
        client.messages.create(body=body, from_=st.secrets["TWILIO_FROM_NUMBER"], to="+256XXXXXXXXX")
        return True
    except:
        return False

# PushOver notification alert
def send_push_alert(site, level, messages):
    """
    Sends a high-priority push notification via Pushover.
    Supports 'Emergency' priority which bypasses silent mode.
    """
    url = "https://api.pushover.net/1/messages.json"
    
    # Logic: If CRITICAL, use emergency priority (2) with 30-sec retries
    # If we use priority=2, the ranger’s phone will keep screaming until they tap "Acknowledge" in the app. 
    # The system can even notify you if they haven't seen it after 5 minutes.
    priority = 2 if level == "CRITICAL" else 1
    
    data = {
        "token": st.secrets["PUSHOVER_API_TOKEN"],
        "user": st.secrets["PUSHOVER_USER_KEY"],
        "title": f"🔥 {level} FIRE RISK: {site}",
        "message": "\n".join(messages),
        "priority": priority,
        "sound": "siren" if level == "CRITICAL" else "climb",
        "expire": 3600,   # Retry for 1 hour
        "retry": 30       # Retry every 30 seconds until acknowledged
    }

    try:
        response = requests.post(url, data=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Pushover Error: {e}")
        return False

# WhatsApp notification alert
def send_whatsapp_alert(site, level, messages):
    """
    Sends a WhatsApp message via Twilio.
    Note: Recipient must have 'opted-in' to the Twilio sandbox for testing.
    """
    try:
        client = Client(st.secrets["TWILIO_ACCOUNT_SID"], st.secrets["TWILIO_AUTH_TOKEN"])
        
        # Crafting a high-impact message
        header = "🔥 *FIRELENS CRITICAL ALERT*" if level == "CRITICAL" else "⚠️ *FIRELENS ADVISORY*"
        body = f"{header}\n\n*Site:* {site}\n*Risk:* {level}\n\n*Details:*\n" + "\n".join([f"- {m}" for m in messages])
        
        message = client.messages.create(
            from_=st.secrets["TWILIO_WHATSAPP_FROM"],
            body=body,
            to=st.secrets["TWILIO_WHATSAPP_TO"]
        )
        return True
    except Exception as e:
        print(f"WhatsApp Error: {e}")
        return False

# Master dispatch message function
def broadcast_all_channels(site, level, messages):
    """
    MASTER DISPATCH: Sends to all active channels simultaneously.
    """
    results = {}
    # 1. Real-time Chat
    results['Telegram'] = send_telegram_alert(site, level, messages)[0]
    
    # 2. Critical Mobile Push
    results['Push (Pushover)'] = send_push_alert(site, level, messages)
    
    # 3. High-Reliability SMS
    results['SMS (Twilio)'] = send_sms_alert(site, level, messages)
    
    # 4. Formal Log (Email)
    results['Email (SMTP)'] = send_email_alert(site, level, messages)

    # 5. WhatsApp notification alert
    results['WhatsApp'] = send_whatsapp_alert(site, level, messages)
        
    # Push notifications (using Streamlit's toast for web-push feel)
    st.toast(f"BROADCAST ACTIVE: {level} risk at {site}", icon="📢")
    
    return results