# image_utils.py

import os
import requests
import shutil
import json
from pathlib import Path
from PIL import Image
from io import BytesIO

import matplotlib.pyplot as plt

from src.utils import (
    json_utils,
    sys_utils
)


def fetch_images(file_path, json_output_path, api_key):
    data = json.loads(Path(file_path).read_text())

    updated_data = []
    fetched_data = []  

    for item in data:
        response = send_request(item['id'], api_key)
        
        if response['status'] == 'success' and response['output']:
            try:
                download_images(response['output'], f'./output/images/{item["id"]}')
                response['meta'] = get_meta_data(item['id'], Path(file_path).parent)
                fetched_data.append(response)
            except Exception as e:
                print(f"Error downloading images: {e}")
            finally:
                updated_data.append(item)

        elif response['status'] == 'processing':
            print(f"Image not ready. Try again at {item.get('available')}")
            updated_data.append(item)
        else:
            updated_data.append(item)

    Path(file_path).write_text(json.dumps(updated_data, indent=4))

    for fetched_item in fetched_data:
        json_utils.append_to_json(fetched_item, json_output_path)


def send_request(id, api_key):
    url = f"https://stablediffusionapi.com/api/v3/fetch/{id}" 
    headers = {'Content-Type': 'application/json'}
    data = {"key": api_key}
    return requests.post(url, headers=headers, json=data).json()


def download_images(image_urls, output_path):
    for url in image_urls:
        filename = os.path.basename(url)
        image_download(url, f'{output_path}/{filename}')
        print(f"Downloaded {url}")


def get_meta_data(id, base_path):
    json_path = base_path / f"{id}/json/{id}.json"
    data = json.loads(json_path.read_text())
    return data.get('meta', {})
