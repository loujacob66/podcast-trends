import json

def save_to_json(records, path):
    with open(path, "w") as f:
        json.dump(records, f, indent=2)

def load_from_json(path):
    with open(path, "r") as f:
        return json.load(f)
