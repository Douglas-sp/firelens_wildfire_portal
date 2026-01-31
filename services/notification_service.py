import streamlit as st
import smtplib
import pandas as pd  # Added missing import
from email.message import EmailMessage
from twilio.rest import Client
import requests
from utils.logger import log_dispatch
from utils.contact_manager import load_contacts

# Telegram alert - Updated to accept individual chat_id
def send_telegram_alert(site, level, messages, chat_id=None):
    token = st.secrets["TELEGRAM_BOT_TOKEN"]
    # If no specific ID provided, use the default from secrets
    target_id = chat_id if chat_id else st.secrets["TELEGRAM_CHAT_ID"]
    
    text = f"🚨 *{level} FIRE RISK: {site}*\n" + "\n".join([f"• {m}" for m in messages])
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={target_id}&text={text}&parse_mode=Markdown"
    try:
        res = requests.get(url)
        return res.status_code == 200, "Sent"
    except Exception as e:
        return False, str(e)

# Email alert
def send_email_alert(site, level, messages, recipient_email=None):
    msg = EmailMessage()
    msg.set_content(f"FireLens Alert for {site}\nRisk Level: {level}\n\nDetails:\n" + "\n".join(messages))
    msg['Subject'] = f"🔥 {level} Fire Risk Alert - {site}"
    msg['From'] = st.secrets["EMAIL_SENDER"]
    # Use directory email if provided, else fallback to your default
    msg['To'] = recipient_email if recipient_email else "wamaniray@uwa.go.ug"

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(st.secrets["EMAIL_SENDER"], st.secrets["EMAIL_PASSWORD"])
            smtp.send_message(msg)
        return True
    except:
        return False

# SMS alert
def send_sms_alert(site, level, messages, recipient):
    try:
        client = Client(st.secrets["TWILIO_ACCOUNT_SID"], st.secrets["TWILIO_AUTH_TOKEN"])
        body = f"FireLens {level}: {site}. Check portal for coords."
        client.messages.create(body=body, from_=st.secrets["TWILIO_FROM_NUMBER"], to=recipient)
        return True
    except:
        return False

# PushOver alert - Updated to accept individual user_key
def send_push_alert(site, level, messages, user_key=None):
    url = "https://api.pushover.net/1/messages.json"
    priority = 2 if level == "CRITICAL" else 1
    # Use directory key if provided, else fallback to secrets
    target_user = user_key if user_key else st.secrets["PUSHOVER_USER_KEY"]
    
    data = {
        "token": st.secrets["PUSHOVER_API_TOKEN"],
        "user": target_user,
        "title": f"🔥 {level} FIRE RISK: {site}",
        "message": "\n".join(messages),
        "priority": priority,
        "sound": "siren" if level == "CRITICAL" else "climb",
        "expire": 3600, "retry": 30
    }
    try:
        response = requests.post(url, data=data)
        return response.status_code == 200
    except:
        return False

# WhatsApp alert
def send_whatsapp_alert(site, level, messages, recipient):
    try:
        client = Client(st.secrets["TWILIO_ACCOUNT_SID"], st.secrets["TWILIO_AUTH_TOKEN"])
        header = "🔥 *FIRELENS CRITICAL ALERT*" if level == "CRITICAL" else "⚠️ *FIRELENS ADVISORY*"
        body = f"{header}\n\n*Site:* {site}\n*Risk:* {level}\n\n*Details:*\n" + "\n".join([f"- {m}" for m in messages])
        client.messages.create(from_=st.secrets["TWILIO_WHATSAPP_FROM"], body=body, to=recipient)
        return True
    except:
        return False

def broadcast_to_directory(selected_site, level, messages):
    contacts = load_contacts()
    relevant_contacts = contacts[
        (contacts['Active'] == True) & 
        (contacts['Assigned_Sites'].str.contains(selected_site, na=False) | 
         contacts['Assigned_Sites'].str.contains("ALL", na=False))
    ]
    
    report = []
    for _, person in relevant_contacts.iterrows():
        channels_ok = []
        
        # 1. SMS
        if pd.notna(person.get('SMS_Phone')) and send_sms_alert(selected_site, level, messages, person['SMS_Phone']):
            channels_ok.append("SMS")
        
        # 2. WhatsApp
        if pd.notna(person.get('WA_Phone')) and send_whatsapp_alert(selected_site, level, messages, person['WA_Phone']):
            channels_ok.append("WA")
            
        # 3. Telegram (Passing the ID from the CSV)
        if pd.notna(person.get('Telegram_ID')) and send_telegram_alert(selected_site, level, messages, person['Telegram_ID'])[0]:
            channels_ok.append("TG")

        # 4. Pushover
        if pd.notna(person.get('Pushover_Key')) and send_push_alert(selected_site, level, messages, person['Pushover_Key']):
            channels_ok.append("Push")
            
        # 5. Email
        if pd.notna(person.get('Email')) and send_email_alert(selected_site, level, messages, person['Email']):
            channels_ok.append("Email")

        report.append({
            "Name": person['Name'],
            "Status": f"✅ {', '.join(channels_ok)}" if channels_ok else "❌ All Failed"
        })
    
    # --- Converting List to Dictionary for the Logger ---
    log_report = {item['Name']: item['Status'] for item in report}
    
    log_dispatch(
        site=selected_site, 
        level=level, 
        recipients_count=len(relevant_contacts), 
        channel_report=log_report
    )
    
    return report