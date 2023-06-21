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
        data = json.load(f)

    updated_data = []
    for item in data:
        url = f"https://stablediffusionapi.com/api/v3/fetch/{item['id']}"
        headers = {'Content-Type': 'application/json'}
        post_data = json.dumps({"key": api_key})

        response = requests.post(url, headers=headers, data=post_data)
        response_data = response.json()

        if response_data.get('status') == 'success' and response_data.get('output'):
            output_path = f'./output/images/{item["id"]}'
            try:
                for image_url in response_data['output']:
                    image_download(image_url, f'{output_path}/{os.path.basename(image_url)}')
                    print(f"Successfully downloaded image from {image_url}")
            except Exception as e:
                print(f"An error occurred while downloading images: {e}")
                updated_data.append(item)
        elif response_data.get('status') == 'processing':
            print(f"Image isn't ready to fetch yet. Try again at {item.get('available')}")
            updated_data.append(item)
        else:
            updated_data.append(item)

    with open(file_path, 'w') as f:
        json.dump(updated_data, f)

