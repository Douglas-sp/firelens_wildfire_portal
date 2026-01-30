import pandas as pd
import os
from datetime import datetime, timezone, timedelta

LOG_DIR = "logs"

def log_dispatch(site, level, recipients_count, channel_report):
    """
    Records dispatch details into a monthly CSV file.
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # 1. Generate filename based on current month (EAT Time)
    eat_now = datetime.now(timezone(timedelta(hours=3)))
    filename = f"{LOG_DIR}/dispatch_log_{eat_now.strftime('%Y_%m')}.csv"
    
    # 2. Prepare the data row
    # Summarize channel status (e.g., "Telegram: OK, SMS: OK")
    status_summary = ", ".join([f"{k}: {v}" for k, v in channel_report.items()])
    
    new_entry = {
        "Timestamp": eat_now.strftime("%Y-%m-%d %H:%M:%S"),
        "Site": site,
        "Risk_Level": level,
        "Recipients": recipients_count,
        "Channel_Status": status_summary
    }
    
    # 3. Append to CSV
    df = pd.DataFrame([new_entry])
    file_exists = os.path.isfile(filename)
    
    # mode='a' appends, header=False prevents repeating headers
    df.to_csv(filename, mode='a', index=False, header=not file_exists)
    return filename
    