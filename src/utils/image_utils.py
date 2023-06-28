import os
import requests
import shutil
import json
import math
import textwrap
import matplotlib.pyplot as plt
from PIL import Image
from IPython.display import display
from io import BytesIO


def img_to_grid(path, save_path, dpi=72, unique_meta=False, width=3):
    with open(path, 'r') as f:
        data = json.load(f)

    # Determine the grid size based on the length of the data
    total_images = len(data)
    # Adjust width if total number of images is less than the default width
    width = min(width, total_images)
    height = math.ceil(total_images / width)

    # Calculate figure size (in inches) based on desired DPI and pixel dimensions
    fig_width_in = 3000 / dpi  # Max width in inches
    fig_height_in = (fig_width_in / width) * height  # Proportional height

    # Calculate font size and wrap length based on width
    font_size = 10 * (3 / width)  # Increase font size when there are fewer columns
    wrap_length = int(0.2 * (3000 / width))  # Approx. 20% of the image's pixel width

    fig, axs = plt.subplots(height, width, figsize=(fig_width_in, fig_height_in))
    keys = ["guidance_scale", "strength", "seed", "steps", "H", "W"]
    seen_meta = {}

    for i, ax in enumerate(axs.flatten()):
        if i < total_images:
            entry = data[i]
            image_url = entry['output'][0]
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
            ax.imshow(img)
            ax.axis('off')

            meta_info = {k: entry['meta'][k] for k in keys if k in entry['meta']}

            if unique_meta:
                meta_info = {k: v for k, v in meta_info.items() if k not in seen_meta or seen_meta[k] != v}
                seen_meta.update(meta_info)

            meta_info_str = ', '.join([f"{k}: {v}" for k, v in meta_info.items()])
            wrapped_meta_info = textwrap.fill(meta_info_str, wrap_length)
            ax.set_title(wrapped_meta_info, fontsize=font_size)

    # Turn off axes for extra subplots if total_images is not a perfect square
    if total_images < width * height:
        for ax in axs.flatten()[total_images:]:
            ax.axis('off')

    plt.tight_layout()
    plt.savefig(save_path, dpi=dpi)


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

