import os
import json
import requests
import time
from urllib.parse import urlparse

class SuperImageFetcher:

    def __init__(self, path, pause_sec, api_key):
        self.path = path
        self.pause_sec = pause_sec
        self.api_key = api_key

    def download_img(self, fetch_url, path):
        payload = json.dumps({
            "key": self.api_key
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(fetch_url, headers=headers, data=payload)
        data = response.json()
        if data.get('status') == 'success':
            img_url = data.get('output', [None])[0]  # Assume the first item in 'output' is the image URL
            if img_url:
                img_response = requests.get(img_url)
                with open(path, 'wb') as f:
                    f.write(img_response.content)

    def get_fetch_result_value(self, master_json_path):
        fetch_results = []
        with open(master_json_path, 'r') as json_file:
            for line in json_file:
                data = json.loads(line)
                fetch_result = data.get('fetch_result', None)
                file_ext = data.get('meta', {}).get('ext', '')
                if fetch_result:
                    fetch_results.append((fetch_result, file_ext))
        return fetch_results

    def fetch_images(self):
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if file == "master.json":
                    master_json_path = os.path.join(root, file)
                    fetch_data = self.get_fetch_result_value(master_json_path)
                    for fetch_url, file_ext in fetch_data:
                        folder_name = os.path.basename(root)
                        unique_index = 1
                        while True:
                            new_filename = f"{folder_name}_fetched-{str(unique_index).zfill(2)}.{file_ext}"
                            new_filepath = os.path.join(root, new_filename)
                            if not os.path.exists(new_filepath):
                                self.download_img(fetch_url, new_filepath)
                                time.sleep(self.pause_sec) # Sleep for 'pause_sec' seconds
                                break
                            unique_index += 1
