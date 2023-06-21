import os
from PIL import Image
from pathlib import Path
from psd_tools import PSDImage
from src.utils.sys_utils import create_dirs


class ImageConverter:
    """
    Class to convert images to a specified format, size, and color space.

    Attributes:
    source (str): Path of the source image or directory containing images.
    output_folder (str, optional): Folder where the converted images will be saved. If not provided, images are saved in a subdirectory of the source directory named after the target format.
    target_format (str, optional): Target image format, can be 'JPEG', 'PNG', etc. Default is 'JPEG'.
    size (tuple, optional): Target image size as a tuple (width, height). Default is None.
    color_space (str, optional): Target color space. Can be 'RGB' or 'CMYK'. Default is None.
    recursive (bool, optional): Flag to indicate whether to recursively convert images in subdirectories. Default is False.
    """

    def __init__(self, source, target_format='JPEG', size=None, color_space=None, recursive=False, output_folder=None):
        self.source = source
        self.output_folder = output_folder
        self.target_format = target_format
        self.size = size
        self.color_space = color_space
        self.recursive = recursive

    def convert(self):
        """Start the image conversion process."""

        if self.output_folder is None:
            self.output_folder = Path(self.source) / self.target_format.lower()

        create_dirs([self.output_folder])

        if os.path.isdir(self.source):
            self._convert_images_in_folder()
        else:
            self._convert_single_image(self.source)

    def _convert_images_in_folder(self):
        for foldername, _, filenames in os.walk(self.source):
            for filename in filenames:
                if filename.lower().endswith(('.psd', '.jpeg', '.jpg', '.png', '.bmp', '.gif', '.tiff')):
                    img_path = os.path.join(foldername, filename)
                    self._convert_single_image(img_path)
            if not self.recursive:
                break

    def _convert_single_image(self, image_path):
        if image_path.lower().endswith('.psd'):
            psd = PSDImage.open(image_path)
            img = psd.composite()
        else:
            img = Image.open(image_path)

        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            img = img.convert('RGBA')

        if self.size:
            img = img.resize(self.size)

        if self.color_space:
            img = self._convert_color_space(img)

        filename = os.path.basename(image_path)
        base_filename, _ = os.path.splitext(filename)
        
        if self.size:
            size_suffix = f"_{self.size[0]}x{self.size[1]}"
        else:
            size_suffix = ""
        
        if self.color_space:
            color_suffix = f"_{self.color_space}"
        else:
            color_suffix = ""
            
        target_filename = f"{base_filename}{color_suffix}{size_suffix}.{self.target_format.lower()}"

        target_path = os.path.join(self.output_folder, target_filename)

        img.save(target_path, format=self.target_format)
        print(f"Converted image saved at: {target_path}")

    def _convert_color_space(self, img):
        target_color_space = self.color_space.upper()

        if target_color_space == 'CMYK' and img.mode != 'CMYK':
            return img.convert('CMYK')
        elif target_color_space == 'RGB' and img.mode != 'RGB':
            return img.convert('RGB')

        return img
