import json
from pathlib import Path
import os

def image_to_yml(directory):
    yml_str = "init_image:\n"
    
    # Use os.walk to iterate over all files in directory and its subdirectories
    for root, _, files in os.walk(directory):
        for file in files:
            # Check if the file is an image (assuming only .jpg, .jpeg, .png files are images)
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Concatenate the root directory and file name to get the full file path
                full_file_path = os.path.join(root, file)
                # Add the file path to the YAML string
                yml_str += f"  - \"{full_file_path}\"\n"
    return yml_str


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

