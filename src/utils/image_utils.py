import os
import requests
import shutil
import json


def image_download(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        filename = os.path.basename(url) if not os.path.basename(path) else os.path.basename(path)
        full_path = os.path.join(os.path.dirname(path), filename)

        with open(full_path, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)

        return full_path
    else:
        print(f"Error downloading image: {response.status_code} - {response.text}")
        return None


def fetch_images(file_path, api_key):
    with open(file_path, 'r') as f:
        for item in json.load(f):
            response = requests.post(
                f"https://stablediffusionapi.com/api/v3/fetch/{item['id']}",
                headers={'Content-Type': 'application/json'},
                data=json.dumps({"key": api_key})
            )
            
            if response.status_code != 200:
                continue

            for image_url in response.json()['output']:
                image_download(image_url, f'./output/images/{item["id"]}/{os.path.basename(image_url)}')

