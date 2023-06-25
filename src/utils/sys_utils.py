import os
from pathlib import Path
import zipfile
import shutil
from dotenv import load_dotenv
from docx import Document
from datetime import datetime


def stable_sync(src, dst):
    src, dst = Path(src), Path(dst)
    if not src.exists():
        print(f"Source folder {src} does not exist")
        return

    timestamp = datetime.now().strftime("%m%d_%H%M")
    dst = dst / timestamp
    dst.mkdir(parents=True)

    for item in src.iterdir():
        if item.is_dir():
            shutil.copytree(str(item), str(dst / item.name))
        else:
            shutil.copy2(str(item), str(dst / item.name))

    src.rename(src.parent / timestamp)


ENV_VARIABLES = [
    'OPENAI_API_KEY',
    'STABLE_API_KEY',
    'UCARE_API_KEY_PUBLIC',
    'UCARE_API_KEY_SECRET',
    'OUT_PATH',
    'IN_PATH',
    'CONFIG_PATH'
]


def load_env_file(env_file_path, print_details=True):
    """Loads environment variables from a file and prints their details."""

    shutil.copy(env_file_path, '.env')
    load_dotenv()
    env_values = {var: os.getenv(var) for var in ENV_VARIABLES}

    if print_details:
        for var, value in env_values.items():
            print(f'{var}: {value}')

    return env_values


def str2list(s, ignore_commas=False):
    if ignore_commas:
        return [s]
    if s.replace(',','').replace('.','').isdigit():
        return [str(i.strip()) for i in s.split(',')]
    return [s]


def docx_to_txt(docx_path):
    """Converts a .docx file into a .txt file."""

    doc = Document(docx_path)
    text = '\n'.join(paragraph.text for paragraph in doc.paragraphs)
    txt_path = os.path.splitext(docx_path)[0] + '.txt'

    with open(txt_path, 'w') as txt_file:
        txt_file.write(text)

    return txt_path


def get_files_in_folder(folder_path, ext=''):
    """Returns a list of filenames in a folder with the given extension."""

    return [
        os.path.splitext(file)[0] 
        for file in os.listdir(folder_path) 
        if file.endswith(ext)
    ]


def create_dirs(dirs):
    """Creates directories if they don't already exist."""

    if isinstance(dirs, str):  # Handle single string input
        dirs = [dirs]

    for output_dir in dirs:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    

def zip_folder(folder_path, output_filename, ext=None):
    """Creates a zip file from a folder."""

    with zipfile.ZipFile(output_filename.rstrip(".zip") + ".zip", 'w') as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                if ext is None or file.endswith(ext):
                    zipf.write(
                        os.path.join(root, file), 
                        arcname=os.path.relpath(
                            os.path.join(root, file), 
                            folder_path
                        )
                    )
