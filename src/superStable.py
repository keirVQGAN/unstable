from src.utils.image_upload import ImageUploader
import requests
import json
import time
import os

class APIUploader:

    def __init__(self, stable_api_key, output_dir='./output/images/'):
        self.stable_api_key = stable_api_key
        self.image_uploader = ImageUploader()
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def upload_and_process(self, img_path, delay_sec=5):
        # Upload the image and get the response URL
        response_url = self.image_uploader.upload_img(img_path)

        # Prepare the API payload with the response URL
        payload = json.dumps({
            "key": self.stable_api_key,
            "url": response_url,
            "scale": 3,
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
        # Iterate through all the files in the folder
        for filename in os.listdir(folder_path):
            # Check if the file is an image (adjust the condition as needed)
            if filename.endswith(".jpg"):
                # Construct the full path to the image
                img_path = os.path.join(folder_path, filename)
                
                # Upload and process the image
                api_response = self.upload_and_process(img_path, delay_sec)
                
                # Print the API response
                print(api_response)
