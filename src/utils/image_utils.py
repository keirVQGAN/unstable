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


def create_web_files(path, bg_color, dir_name="web_files"):
    with open(path, 'r') as f:
        data = json.load(f)

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    with open(os.path.join(dir_name, 'index.html'), 'w') as file:
        file.write(generate_html(data, bg_color))

    with open(os.path.join(dir_name, 'style.css'), 'w') as file:
        file.write(generate_css(bg_color))

    with open(os.path.join(dir_name, 'main.js'), 'w') as file:
        file.write(generate_js(data))

def generate_html(data, bg_color):
    common_meta = {k: data[0]['meta'][k] for k in ["guidance_scale", "strength", "seed", "steps", "H", "W"] if k in data[0]['meta']}
    common_meta['prompt'] = data[0]['meta'].get('prompt', '')  # Add 'prompt' key to common_meta

    unique_meta_list = []

    for entry in data:
        meta_info = {k: entry['meta'][k] for k in ["guidance_scale", "strength", "seed", "steps", "H", "W", "prompt"] if k in entry['meta']}
        unique_meta = {k: v for k, v in meta_info.items() if k not in common_meta or common_meta[k] != v}
        unique_meta_list.append(unique_meta)

    # Start building the HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Image Grid</title>
    <link rel="stylesheet" type="text/css" href="style.css">
</head>
<body style="background-color: {bg_color};">
    <div class="grid">"""

    for i, entry in enumerate(data):
        image_url = entry['output'][0]
        meta_info_str = ', '.join([f"{k}: {v}" for k, v in unique_meta_list[i].items()])
        html += f"""
        <div class="cell" data-url="{image_url}" data-meta="{meta_info_str}" onclick="downloadImage(this)">
            <img src="{image_url}" alt="image">
            <div class="overlay">
                <div class="text">{meta_info_str}</div>
            </div>
        </div>"""

    common_meta_str = ', '.join([f"{k}: {v}" for k, v in common_meta.items()])

    html += f"""
    </div>
    <div class="common-info">
        <p><strong>Common Meta Information:</strong> {common_meta_str}</p>
    </div>
    <script src="main.js"></script>
</body>
</html>"""
    return html

def generate_css(bg_color):
    return f"""
    body {{
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        background-color: {bg_color};
    }}
    .grid {{
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        padding: 50px;
    }}
    .cell {{
        margin: 10px;
        position: relative;
    }}
    .cell img {{
        width: 200px;
        height: 200px;
    }}
    .overlay {{
        position: absolute;
        top: 0;
        bottom: 0;
        left: 0;
        right: 0;
        height: 200px;
        width: 200px;
        opacity: 0;
        transition: .3s ease;
        background-color: black;
    }}
    .cell:hover .overlay {{
        opacity: 0.8;
    }}
    .text {{
        color: white;
        font-size: 12px;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
    }}
    .common-info {{
        max-width: 800px;
        margin: 50px auto;
        padding: 20px;
        border: 1px solid #333;
        border-radius: 5px;
    }}
    """

def generate_js(data):
    return """
    function downloadImage(element) {
        var url = element.getAttribute('data-url');
        var meta = element.getAttribute('data-meta');
        var link = document.createElement('a');
        link.href = url;
        link.download = meta.replace(/, /g, '_') + '.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    """

