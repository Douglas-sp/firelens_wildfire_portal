import pandas as pd
import os

CONTACTS_FILE = "data/contacts.csv"

def load_contacts():
    # If the file doesn't exist, CREATE IT automatically
    if not os.path.exists(CONTACTS_FILE):
        os.makedirs("data", exist_ok=True)
        template = pd.DataFrame(columns=[
            "Name", "Role", "Assigned_Sites", "SMS_Phone", 
            "WA_Phone", "Email", "Telegram_ID", "Pushover_Key", "Active"
        ])
        template.to_csv(CONTACTS_FILE, index=False)
        return template
    
    return pd.read_csv(CONTACTS_FILE)