import requests
import yaml
import time
import json

class StableAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def request(self, call=None, prompt=None, negative_prompt=None, init_image=None, mask_image=None,
                enhance_prompt=None, guidance_scale=None, height=None, width=None, samples=None,
                num_inference_steps=None, self_attention=None, upscale=None, seed=None):
        
        url = f'https://stablediffusionapi.com/api/v3/{call}'
        yaml_file = f'./config/stable/{call}.yml'

        with open(yaml_file, 'r') as f:
            api_options = yaml.safe_load(f)

        api_options.update({
            'prompt': prompt,
            'key': self.api_key,
            'negative_prompt': negative_prompt,
            'init_image': init_image or api_options.get('init_image'),
            'mask_image': mask_image or api_options.get('mask_image'),
            'enhance_prompt': enhance_prompt or api_options.get('enhance_prompt'),
            'guidance_scale': guidance_scale or api_options.get('guidance_scale'),
            'height': height or api_options.get('height'),
            'width': width or api_options.get('width'),
            'samples': samples or api_options.get('samples'),
            'num_inference_steps': num_inference_steps or api_options.get('num_inference_steps'),
            'self_attention': self_attention or api_options.get('self_attention'),
            'upscale': upscale or api_options.get('upscale'),
            'seed': seed or api_options.get('seed')
        })

        headers = {"Content-Type": "application/json"}
        response = requests.post(url=url, headers=headers, json=api_options)

        try:
            response_data = response.json()
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from response. Status code: {response.status_code}, Response text: {response.text}")
            return None

        return response_data
