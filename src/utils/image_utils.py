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


def img_to_grid(path, save_path, dpi=72, unique_meta=False, width=3):
    with open(path) as f:
        data = json.load(f)

    total = len(data)
    width = min(width, total) 
    height = math.ceil(total / width)

    fig_width = 3000 / dpi  
    fig_height = (fig_width / width) * height

    font_size = 10 * (3 / width)
    wrap_length = int(0.2 * (3000 / width))

    fig, axs = plt.subplots(height, width, figsize=(fig_width, fig_height))
    keys = ["guidance_scale", "strength", "seed", "steps", "H", "W"]
    seen_meta = {}

    for i, ax in enumerate(axs.flatten()):
        if i < total:
            entry = data[i]
            img = Image.open(BytesIO(requests.get(entry['output'][0]).content))
            ax.imshow(img)
            ax.axis('off')

            meta = {k: entry['meta'][k] for k in keys if k in entry['meta']}
            if unique_meta:
                meta = {k: v for k, v in meta.items() if k not in seen_meta or seen_meta[k] != v}
                seen_meta.update(meta)

            meta_str = ', '.join([f"{k}: {v}" for k, v in meta.items()])
            wrapped_meta = textwrap.fill(meta_str, wrap_length)
            ax.set_title(wrapped_meta, fontsize=font_size)

    if total < width * height:
        for ax in axs.flatten()[total:]:
            ax.axis('off')

    plt.tight_layout()
    plt.savefig(save_path, dpi=dpi)


def image_download(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with open(path, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)
        return path
    
    print(f"Error downloading {url}: {response.status_code} - {response.text}")


def web_grid(path, bg_color, dir_name="web_files"):
    with open(path) as f:
        data = json.load(f)

    sys_utils.create_dirs(dir_name) 

    with open(f"{dir_name}/index.html", 'w') as f:
        f.write(generate_html(data, bg_color))

    with open(f"{dir_name}/style.css", 'w') as f:
        f.write(generate_css(bg_color))

    with open(f"{dir_name}/main.js", 'w') as f:
        f.write(generate_js(data))


def generate_html(data, bg_color):
    common_meta = {k: data[0]['meta'][k] for k in ["guidance_scale", "strength", "seed", "steps", "H", "W"] if k in data[0]['meta']}
    common_meta['prompt'] = data[0]['meta'].get('prompt', '')  

    unique_meta_list = []

    for entry in data:
        meta = {k: entry['meta'][k] for k in ["guidance_scale", "strength", "seed", "steps", "H", "W", "prompt"] if k in entry['meta']}
        unique_meta = {k: v for k, v in meta.items() if k not in common_meta or common_meta[k] != v}
        unique_meta_list.append(unique_meta)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Image Grid</title>
      <link rel="stylesheet" href="style.css"> 
    </head>
    <body style="background-color: {bg_color};">
      <div class="grid">
    """

    for i, entry in enumerate(data):
        img_url = entry['output'][0]
        meta_str = ', '.join([f"{k}: {v}" for k, v in unique_meta_list[i].items()])
        html += f"""
        <div class="cell" data-url="{img_url}" data-meta="{meta_str}" onclick="downloadImage(this)">
          <img src="{img_url}">
          <div class="overlay">
            <div class="text">{meta_str}</div>
          </div>
        </div>
        """

    common_meta_str = ', '.join([f"{k}: {v}" for k, v in common_meta.items()])

    html += f"""
      </div>

      <div class="common-info">
        <p><strong>Common Meta:</strong> {common_meta_str}</p> 
      </div>

      <script src="main.js"></script>

    </body>
    </html>
    """

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
      let url = element.getAttribute('data-url');
      let meta = element.getAttribute('data-meta');
      let link = document.createElement('a');
      link.href = url;
      link.download = meta.replace(/, /g, '_') + '.png';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  """
