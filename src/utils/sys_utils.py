import os
import shutil
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime
from dotenv import load_dotenv

def sort_files(directory):
    for path in Path(directory).iterdir():
        if path.is_file():
            prefix = path.stem.split('_')[0]
            destination = Path(directory) / prefix
            destination.mkdir(exist_ok=True)
            path.rename(destination / path.name)
        elif path.is_dir():
            sort_files(path)
            

def load_env_file(env_file_path, print_details=True):
    shutil.copy(env_file_path, '.env')
    load_dotenv()
    
    ENV_VARS = [
        'OPENAI_API_KEY',
        'STABLE_API_KEY',
        'UCARE_API_KEY_PUBLIC',
        'UCARE_API_KEY_SECRET',
        'OUT_PATH',
        'IN_PATH',
        'CONFIG_PATH'
    ]

    env_values = {var: os.getenv(var) for var in ENV_VARS}
    
    if print_details:
        for var, value in env_values.items():
            print(f"{var}: {value}")
            
    return env_values

def str2list(s, ignore_commas=False):
    if ignore_commas:
        return [s]
    if s.replace(',','').replace('.','').isdigit():
        return [str(i.strip()) for i in s.split(',')]
    return [s]

def create_dirs(dirs):
    if isinstance(dirs, str):
        dirs = [dirs]
        
    for path in dirs:
        Path(path).mkdir(parents=True, exist_ok=True)
        
def zip_folder(folder_path, output_filename):
    with ZipFile(output_filename, 'w') as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                zipf.write(
                    os.path.join(root, file),
                    arcname=os.path.relpath(
                        os.path.join(root, file), 
                        folder_path
                    )
                )
