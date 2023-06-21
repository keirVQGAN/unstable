import requests
import yaml
import time
import json
import itertools
from src.utils.response_processor import ResponseProcessor

class StableAPI:

    BASE_URL = 'https://stablediffusionapi.com/api'
    CONFIG_PATH = './config/stable'
    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, api_key=None):
        self.api_key = api_key

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
        url = f'{self.BASE_URL}/v5/controlnet' if call == 'controlnet' else f'{self.BASE_URL}/v3/{call}'
        yaml_file = f'{self.CONFIG_PATH}/controlnet.yml' if call == 'controlnet' else f'{self.CONFIG_PATH}/{call}.yml'

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
            if debug:
                self.debug_message(combo, response_data)
            responses.append(response_data)
            status = response_data['status']
            print(status)
        return responses

    @staticmethod
    def debug_message(combo, response_data):
        print('Rendering: ' + str(combo))
        status = response_data['status']
        if status == 'success':
            print(str(response_data['output']) + '\n')
        elif status == 'processing':
            print('Processing Image. Run fetch after ' + str(round(float(response_data['eta']), 2)) + ' sec.\n')
