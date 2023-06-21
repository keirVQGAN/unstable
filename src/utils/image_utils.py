import os
import requests
import shutil

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

