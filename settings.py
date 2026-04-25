import json
import os

SETTINGS_FILE = "data/settings.json"

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {
            "company_name": "",
            "address": "",
            "phone": "",
            "email": "",
            "logo_path": "",
            "moms": 25,
            "payment_info": "",
            "payment_terms": "30 dagar netto",
            "qr_path": ""
        }

    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)