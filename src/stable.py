import os
import requests
import yaml
import time
import json
import itertools
from src.utils.image_upload import ImageUploader
from src.utils.response_processor import ResponseProcessor
from src.utils.image_utils import fetch_images
from src.utils.sys_utils import str2list

class StableAPI:
    BASE_URL = 'https://stablediffusionapi.com/api'
    CONFIG_PATH = './config/stable'
    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, api_key=None):
        self.api_key = api_key
        self.uploader = ImageUploader()

    @staticmethod
    def _load_yaml(file):
        with open(file, 'r') as f:
            return yaml.safe_load(f)

    def _make_request(self, url, json_body):
        response = requests.post(url=url, headers=self.HEADERS, json=json_body)
        try:
            return response.json()
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from response. Status code: {response.status_code}, Response text: {response.text}")
            return None

    def request(self, call=None, **kwargs):
        url = f'{self.BASE_URL}/v3/{call}'
        api_options = self._load_yaml(f'{self.CONFIG_PATH}/{call}.yml')
        api_options.update(kwargs)
        api_options['key'] = self.api_key
        return self._make_request(url, api_options)

    def get_responses(self, options_dict, debug=False):
        combos = [dict(zip(options_dict, v)) for v in itertools.product(*options_dict.values())]
        responses = [self.request(**combo) for combo in combos]
        if debug:
            for combo, response_data in zip(combos, responses):
                self.debug_message(combo, response_data)
        return responses, responses[0]['status']

    @staticmethod
    def debug_message(combo, response_data):
        print(f'Rendering: {combo}')
        status = response_data['status']
        if status == 'success':
            print(f"{response_data['output']}\n")
        elif status == 'processing':
            print(f'Processing Image. Run fetch after {round(float(response_data["eta"]), 2)} sec.\n')

    def upload_and_set_image(self, options, image_key):
        paths = options.get(image_key)

        if not paths:
            return

        if not isinstance(paths, list):
            paths = [paths]

        uploaded_images = []
        for path in paths:
            if os.path.isfile(path):
                print(f'uploading {image_key}: {path}')
                uploaded_images.append(self.uploader.upload_img(path))
            else:
                raise FileNotFoundError(f"No file found at {path}")
        options[image_key] = uploaded_images

    def set_options(self, yaml_path):
        options = self.yml_to_options(yaml_path)

        if options.get('init_image'):
            self.upload_and_set_image(options, 'init_image')

        if options.get('call') == "inpaint" and options.get('mask_image'):
            self.upload_and_set_image(options, 'mask_image')

        return options

    @staticmethod
    def yml_to_options(filename):
        with open(filename, 'r') as stream:
            config = yaml.safe_load(stream)

        options_batch = {}
        for key, value in config.items():
            if key in ["prompt", "init_image"]:
                options_batch[key] = [p for p in value]
            else:
                options_batch[key] = str2list(value) if isinstance(value, str) else value
        return options_batch

    def process_responses(self, results):
        for response_data in results:
            ResponseProcessor(response_data).process()
            time.sleep(1)

    def fetch_images_if_processing(self, status):
        if status == 'processing':
            fetch_images('/content/unstable/output/images/processing.json', self.api_key)

    def fetch_images_from_path(self, file_path, stable_debug):
        if stable_debug:
            print('Fetching Images from' + file_path)
        fetch_images(file_path, self.api_key)
