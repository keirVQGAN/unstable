import os
import shutil
import subprocess

class Installer:
    def __init__(self, env_file_path='/content/drive/MyDrive/oracle/.env'):
        self.env_file_path = env_file_path

    def install_uncommon(self):
        if os.path.isdir('/content/sample_data'):
            shutil.rmtree('/content/sample_data')

        os.chdir('/content/unstable/')
        try: 
            import openai
        except ImportError:
            print("Installing uncommon...")
            subprocess.check_call(["pip", "install", "-r", "./requirements.txt"])
        
        print("Installed unstable")
        
        from src.utils.sys_utils import load_env_file
        self.env_values = load_env_file(self.env_file_path, False)

        # Set variables based on the values in env_values dictionary
        self.openai_api_key = self.env_values['OPENAI_API_KEY']
        self.stable_api_key = self.env_values['STABLE_API_KEY']
        self.ucare_api_key_public = self.env_values['UCARE_API_KEY_PUBLIC']
        self.ucare_api_key_secret = self.env_values['UCARE_API_KEY_SECRET']
        self.out_path = self.env_values['OUT_PATH']
        self.in_path = self.env_values['IN_PATH']
        self.config_path = self.env_values['CONFIG_PATH']

        print("Loaded environment")

        # Returning the dictionary of environment variables
        return {
            'openai_api_key': self.openai_api_key,
            'stable_api_key': self.stable_api_key,
            'ucare_api_key_public': self.ucare_api_key_public,
            'ucare_api_key_secret': self.ucare_api_key_secret,
            'out_path': self.out_path,
            'in_path': self.in_path,
            'config_path': self.config_path
        }
