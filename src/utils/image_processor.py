import os
import shutil
import time

from src.utils.image_utils import fetch_images, img_to_grid, web_grid
from src.utils.sys_utils import stable_sync


class ImageProcessor:
    def __init__(self, stable_api_key, processing_json_path='/content/unstable/output/images/processing.json', backup_src='/content/unstable/output/images', backup_dest='/content/drive/MyDrive/unstable/images/output'):
        self.stable_api_key = stable_api_key
        self.processing_json_path = processing_json_path
        self.backup_src = backup_src
        self.backup_dest = backup_dest

    def fetch_processed_image(self, pause=False, pause_sec=20, fetch=True):
        if pause:
            time.sleep(pause_sec)

        if fetch:
            if os.path.isfile(self.processing_json_path):
                fetch_images(self.processing_json_path, self.stable_api_key)
            else:
                print('All images processed')

    def process_web_grid(self, web_grid_paths=None):
        if web_grid_paths:
            web_grid(*web_grid_paths)

    def backup_image(self, image_backup=False):
      stable_sync(self.backup_src, self.backup_dest)
      print('Synced' + self.backup_src, self.backup_dest)

    def create_image_grid(self, image_grid_paths=None):
        if image_grid_paths:
            img_to_grid(*image_grid_paths)
