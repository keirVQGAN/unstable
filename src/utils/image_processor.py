#src.utils.image_processor.py
import os
import shutil
import time
import logging

from src.utils.image_utils import img_to_grid, web_grid, image_download, fetch_images
from src.utils.sys_utils import stable_sync


class ImageProcessor:
    def __init__(self, stable_api_key, processing_json_path='/content/unstable/output/images/processing.json',
                 backup_src='/content/unstable/output/images', backup_dest='/content/drive/MyDrive/unstable/images/output',
                 debug=False):
        self.stable_api_key = stable_api_key
        self.processing_json_path = processing_json_path
        self.backup_src = backup_src
        self.backup_dest = backup_dest
        self.debug = debug
        self.logger = self._configure_logger()

    def _configure_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def fetch_processed_image(self, json_output_path, pause=False, pause_sec=20, fetch=True):
        if pause:
            time.sleep(pause_sec)

        if fetch:
            if os.path.isfile(self.processing_json_path):
                fetch_images(self.processing_json_path, json_output_path, self.stable_api_key)
            else:
                self.logger.info('All images processed')

    def process_web_grid(self, web_grid_paths=None):
        if web_grid_paths:
            try:
                web_grid(*web_grid_paths)
            except FileNotFoundError as e:
                self.logger.error('Error during web grid processing: %s', e)

    def backup_image(self, image_backup=False):
        try:
            stable_sync(self.backup_src, self.backup_dest)
            if self.debug:
              self.logger.info('Synced %s %s', self.backup_src, self.backup_dest)
        except Exception as e:
            self.logger.error('Error during backup: %s', e)

    def create_image_grid(self, image_grid_paths=None):
        if image_grid_paths:
            try:
                img_to_grid(*image_grid_paths)
            except Exception as e:
                self.logger.error('Error during image grid creation: %s', e)
