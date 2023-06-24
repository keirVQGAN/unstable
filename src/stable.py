import requests
import yaml
import time
import json
import itertools
from src.utils.response_processor import ResponseProcessor
from src.utils.image_utils import fetch_images
from src.utils.image_upload import ImageUploader

class StableAPI:
    BASE_URL = 'https://stablediffusionapi.com/api'
    CONFIG_PATH = './config/stable'
    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, api_key=None):
        self.api_key = api_key
        self.uploader = ImageUploader()

    def yml_to_options(self, filename):
        # Load the options from the yaml file
        with open(filename, 'r') as stream:
            config = yaml.safe_load(stream)

        # Create the options dictionary with loaded inputs
        options_batch = {}

        for key, value in config.items():
            if key == "prompt":
                # Format 'prompt' values accordingly
                options_batch[key] = [p for p in value]
            elif key == "negative_prompt":
                # 'negative_prompt' values can be assigned directly
                options_batch[key] = value
            else:
                # Other key-value pairs are processed here
                options_batch[key] = str2list(value) if isinstance(value, str) else value

        return options_batch

    def _load_yaml(self, file):
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
        yaml_file = f'{self.CONFIG_PATH}/{call}.yml'

        api_options = self._load_yaml(yaml_file)
        api_options.update(kwargs)
        api_options['key'] = self.api_key

        return self._make_request(url, api_options)

    def get_responses(self, options_dict, debug=False):
        keys, values = zip(*options_dict.items())
        combos = [dict(zip(keys, v)) for v in itertools.product(*values)]

        responses = []
        for combo in combos:
            response_data = self.request(**combo)
            self.debug_message(combo, response_data) if debug else None
            responses.append(response_data)
        return responses, response_data['status']

    @staticmethod
    def debug_message(combo, response_data):
        print('Rendering: ' + str(combo))
        status = response_data['status']
        if status == 'success':
            print(str(response_data['output']) + '\n')
        elif status == 'processing':
            print('Processing Image. Run fetch after ' + str(round(float(response_data['eta']), 2)) + ' sec.\n')

    def upload_image(self, image_path):
        return self.uploader.upload_img(image_path)

    def set_options(self, stable_call, init_path=None, mask_path=None):
        stable_calls = [stable_call]
        options = {'call': stable_calls}

        if stable_call in ["img2img", "inpaint"]:
            print(f'uploading init_image: {init_path}')
            init_image = self.upload_image(init_path)
            options['init_image'] = [init_image]

        if stable_call == "inpaint":
            print(f'uploading mask_image: {mask_path}')
            mask_image = self.upload_image(mask_path)  
            options['mask_image'] = [mask_image]

        return options

    def process_responses(self, results):
        for response_data in results:
            processor = ResponseProcessor(response_data)
            status, response, path = processor.process()
            time.sleep(1)
        return status

    def fetch_images_if_processing(self, status):
        if status == 'processing':
            file_path='/content/unstable/output/images/processing.json'
            fetch_images(file_path, self.api_key)

    def fetch_images_from_path(self, file_path, stable_debug):
        if stable_debug:
            print('Fetching Images from' + file_path)
        fetch_images(file_path, self.api_key)
