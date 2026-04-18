import json
import os

ROUTES_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "routes.json")


def load():
    path = os.path.abspath(ROUTES_FILE)
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"routes": []}


def save(data):
    path = os.path.abspath(ROUTES_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
