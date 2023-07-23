import json
from pathlib import Path

def write_to_json(data, path):
    Path(path).write_text(
        json.dumps(data, indent=4, separators=(',', ': '))
    )

def append_to_json(data, path):
    try:
        existing = json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        existing = []
        
    existing.append(data)
    
    write_to_json(existing, path)
