import os
import json
from pyuploadcare import Uploadcare
from pathlib import Path

class ImageUploader:
    """
    Class to upload images and keep track of uploaded images.

    Attributes:
    uploaded_json_path (str): Path of the JSON file that tracks uploaded images.
    """
    
    def __init__(self, uploaded_json_path='/content/drive/MyDrive/unstable/images/uploaded/uploaded.json'):
        public_key = os.environ.get('UCARE_API_KEY_PUBLIC')
        secret_key = os.environ.get('UCARE_API_KEY_SECRET')
        self.uploadcare = Uploadcare(public_key, secret_key)
        self.uploaded_json_path = uploaded_json_path
        Path(self.uploaded_json_path).parent.mkdir(parents=True, exist_ok=True)
        if not Path(self.uploaded_json_path).exists():
            with open(self.uploaded_json_path, 'w') as f:
                json.dump({}, f)

    def upload_img(self, img_path):
        try:
            with open(self.uploaded_json_path, 'r') as f:
                uploaded_files = json.load(f)
        except json.JSONDecodeError:
            with open(self.uploaded_json_path, 'w') as f:
                json.dump({}, f)
            uploaded_files = {}

        if img_path in uploaded_files:
            # print(f"Image at path {img_path} has already been uploaded.")
            return uploaded_files[img_path]
        
        with open(img_path, 'rb') as file_object:
            ucare_file = self.uploadcare.upload(file_object)

        uploaded_files[img_path] = str(ucare_file)

        with open(self.uploaded_json_path, 'w') as f:
            json.dump(uploaded_files, f)

        return str(ucare_file)
