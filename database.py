import json
import os

DB_FILE = "data.json"


def load_data():
    if not os.path.exists(DB_FILE):
        return []

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def is_new(link):
    data = load_data()

    if link in data:
        return False

    data.append(link)

    if len(data) > 500:
        data = data[-500:]

    save_data(data)
    return True
