import os
import requests
import yaml
import time
import json
import itertools
from src.utils.image_upload import ImageUploader
from src.utils.response_processor import ResponseProcessor
from src.utils.sys_utils import str2list


class StableAPI:
    BASE_URL = 'https://stablediffusionapi.com/api'
    CONFIG_PATH = './config/stable'
    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, api_key=None, yaml_path=None, debug=False, delay=1):
        self.api_key = api_key
        self.uploader = ImageUploader()
        self.yaml_path = yaml_path
        self.debug = debug
        self.delay = delay

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

    def set_options(self, yaml_path=None):
        yaml_path = yaml_path or self.yaml_path
        options = self.yml_to_options(yaml_path)

        if options.get('init_image'):
            self.upload_and_set_image(options, 'init_image')

        if options.get('call') == "inpaint" and options.get('mask_image'):
            self.upload_and_set_image(options, 'mask_image')

        return options

    def run(self):
        options = self.set_options()
        responses, status = self.get_responses(options)
        self.process_responses(responses)

    def get_responses(self, options_dict):
        combos = [dict(zip(options_dict, v)) for v in itertools.product(*options_dict.values())]
        responses = [self.request(**combo) for combo in combos]
        if self.debug:
            self.debug_responses(combos, responses)
        return responses, responses[0]['status']

    @staticmethod
    def debug_responses(combos, responses):
        for combo, response_data in zip(combos, responses):
            print(f'Rendering: {combo}')
            status = response_data['status']
            if status == 'success':
                print(f"{response_data['output']}\n")
            elif status == 'processing':
                print(f'Processing Image. Run fetch after {round(float(response_data["eta"]), 2)} sec.\n')

    def upload_and_set_image(self, options, image_key):
        paths = options.get(image_key, [])
        paths = paths if isinstance(paths, list) else [paths]

        uploaded_images = []
        for path in paths:
            if os.path.isfile(path):
                uploaded_images.append(self.uploader.upload_img(path))
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                            full_path = os.path.join(root, file)
                            uploaded_images.append(self.uploader.upload_img(full_path))

        if len(uploaded_images) != len(paths):
            raise FileNotFoundError("Some files not found")
        options[image_key] = uploaded_images

    @staticmethod
    def yml_to_options(filename):
        with open(filename, 'r') as stream:
            config = yaml.safe_load(stream)

        options_batch = {k: str2list(v) if isinstance(v, str) else v for k, v in config.items()}
        return options_batch

    def process_responses(self, results):
        for response_data in results:
            ResponseProcessor(response_data).process()
            time.sleep(self.delay)
