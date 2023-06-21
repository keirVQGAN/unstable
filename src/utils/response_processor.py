from src.utils.json_utils import write_to_json, append_to_json
from src.utils.sys_utils import create_dirs
from src.utils.image_utils import image_download
import datetime, os, json

class ResponseProcessor:
    def __init__(self, response, output_dir='./output/images/'):
        self.response = response
        self.status = response['status']
        self.output_dir = output_dir

    def process(self):
        if self.status == 'success':
            return self.process_success_status()
        elif self.status == 'processing':
            return self.process_processing_status()
        elif self.status in ['error', 'failed']:
            return self.process_error_response()
        else:
            return "Invalid status", self.response, None

    def process_processing_status(self):
        id_directory = self.make_dirs(self.response["id"])
        processing_data = self.get_processing_data()
        self.write_and_append(id_directory, processing_data, 'processing.json')

        return self.response['status'], self.response, os.path.join(id_directory, 'processing.json')

    def process_success_status(self):
        id_directory = self.make_dirs(self.response["id"])
        self.response['date_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.write_and_append(id_directory, self.response, 'master.json')
        self.download_images(self.response['output'], self.response["id"])
        
        return self.response['status'], self.response, os.path.join(id_directory, f'{self.response["id"]}.json')

    def process_error_response(self):
        status = self.response['status']
        message = self.response.get('message', '')
        tips = self.response.get('tips', '')

        print(f"Error: {status}")
        print(f"Message: {message}")
        print(f"Tips: {tips}")

        return status, self.response, None

    def make_dirs(self, id):
        id_directory = os.path.join(self.output_dir, f'{id}/json/')
        create_dirs(id_directory)
        create_dirs(self.output_dir)
        return id_directory

    def get_processing_data(self):
        keys = ['eta', 'fetch_result', 'id']
        processing_data = {key: self.response[key] for key in keys if key in self.response}
        processing_data['available'] = self.calculate_eta(self.response['eta'])
        return processing_data

    def write_and_append(self, id_directory, data, filename):
        write_to_json(self.response, os.path.join(id_directory, f'{self.response["id"]}.json'))
        append_to_json(data, os.path.join(self.output_dir, filename))

    def download_images(self, image_urls, id):
        for image_url in image_urls:
          image_name = os.path.basename(image_url)
          image_download(image_url, os.path.join(self.output_dir, f'{id}/{image_name}'))

    def calculate_eta(self, eta):
        current_time = datetime.datetime.now()
        eta_seconds = datetime.timedelta(seconds=int(eta))
        return (current_time + eta_seconds).time().strftime("%H:%M:%S")
