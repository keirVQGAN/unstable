import json
from pathlib import Path


def write_to_json(data, path):
    Path(path).write_text(json.dumps(data, indent=4, separators=(',', ': ')))


def append_to_json(data, path):
    existing_data = []
    
    try:
        existing_data = json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    existing_data.append(data)
    
    Path(path).write_text(json.dumps(existing_data, indent=4, separators=(',', ': ')))

