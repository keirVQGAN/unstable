from src.utils.image_upload import ImageUploader
from src.utils.image_utils import image_download
import requests
import json
import time
import os
from tqdm import tqdm

class APIUploader:

    def __init__(self, stable_api_key, output_dir='./output/images/', scale=3):
        self.stable_api_key = stable_api_key
        self.image_uploader = ImageUploader()
        self.output_dir = output_dir
        self.scale = scale
        os.makedirs(self.output_dir, exist_ok=True)
        self.processed_urls = set()  # Set to store processed image URLs

    def upload_and_process(self, img_path, delay_sec=5):
        # Upload the image and get the response URL
        response_url = self.image_uploader.upload_img(img_path)

        # Check if the URL has already been processed
        if response_url in self.processed_urls:
            print(f"Skipping file: {img_path} (already processed)")
            return None

        # Add the URL to the set of processed URLs
        self.processed_urls.add(response_url)

        # Prepare the API payload with the response URL
        payload = json.dumps({
            "key": self.stable_api_key,
            "url": response_url,
            "scale": self.scale,
            "webhook": None,
            "face_enhance": False
        })

        # Make the API call
        url = "https://stablediffusionapi.com/api/v3/super_resolution"
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=payload)

        # Delay before the next API call
        time.sleep(delay_sec)

        # Save the API response to master.json
        master_json_path = os.path.join(self.output_dir, 'master.json')
        with open(master_json_path, 'a') as f:
            f.write(response.text + '\n')

        # Process the API response
        api_response = json.loads(response.text)
        if api_response['status'] == 'success':
            # Download the output image
            output_image_url = api_response['output']
            output_image_name = os.path.basename(img_path).rsplit('.', 1)[0] + '_super.' + output_image_url.rsplit('.', 1)[1]
            output_image_path = os.path.join(self.output_dir, output_image_name)
            image_download(output_image_url, output_image_path)

        return api_response

    def process_batch(self, folder_path, delay_sec=5):
        # Get the list of image files in the folder
        image_files = [filename for filename in os.listdir(folder_path) if filename.endswith(".jpg")]

        # Create a progress bar
        progress_bar = tqdm(image_files, desc="Processing Images", unit="image")

        # Iterate through all the image files in the folder
        for filename in progress_bar:
            # Construct the full path to the image
            img_path = os.path.join(folder_path, filename)

            # Check if the output image already exists
            output_image_name = os.path.splitext(filename)[0] + '_super.jpg'
            output_image_path = os.path.join(self.output_dir, output_image_name)
            if os.path.exists(output_image_path):
                progress_bar.set_postfix({"Status": "Skipped", "File": filename})
                continue

            # Upload and process the image
            api_response = self.upload_and_process(img_path, delay_sec)

            # Update the progress bar description
            progress_bar.set_postfix({"Status": api_response["status"], "File": filename})

    def process_directory(self, directory_path, delay_sec=5):
        for root, dirs, _ in os.walk(directory_path):
            for dir in dirs:
                time.sleep(delay_sec * 20)
                folder_path = os.path.join(root, dir)
                print(f'Upscale subfolder: {dir}')
                self.output_dir = os.path.join(self.output_dir, dir)
                os.makedirs(self.output_dir, exist_ok=True)
                self.process_batch(folder_path, delay_sec)
