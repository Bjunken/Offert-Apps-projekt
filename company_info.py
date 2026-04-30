import json
import os
import sys


def get_data_dir():
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    data_dir = os.path.join(base, "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_settings_path():
    return os.path.join(get_data_dir(), "settings.json")


def load_settings():
    path = get_settings_path()

    if not os.path.exists(path):
        return {
            "company_name":  "",
            "address":       "",
            "phone":         "",
            "email":         "",
            "logo_path":     "",
            "moms":          25,
            "payment_info":  "",
            "payment_terms": "30 dagar netto",
            "qr_path":       ""
        }

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(data):
    path = get_settings_path()

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)