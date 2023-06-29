import yaml
import json
import os
import shutil
from datetime import datetime
from src.chatbot import Chatbot
from src.transcript_cleaner import TranscriptCleaner


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()


def clean_transcript(transcript_path, excel_path, student_name, tutor_name, debug=True):
    transcript_cleaner = TranscriptCleaner(
        transcript_path=transcript_path,
        excel_path=excel_path,
        student_name=student_name,
        tutor_name=tutor_name,
        debug=debug
    )

    transcript_clean = transcript_cleaner.clean_transcript()
    pre_notes_clean = transcript_cleaner.clean_pre_tutorial_notes()

    return transcript_clean, pre_notes_clean


def transcript(transcript_path, pre_notes_path, openai_api_key, transcript_yml='/content/unstable/config/transcript/config_transcript.yml', model='gpt-4', count_tokens=False, chat=False, debug=False, tutor_name='Keir Williams', gdrive_backup_transcription='/content/drive/MyDrive/unstable/transcription/output'):
    date_slug = datetime.now().strftime('%m-%d_%H-%M')
    student_name = os.path.basename(transcript_path).replace('.txt', '')
    student_folder = os.path.join(os.getcwd(), 'output/transcripts', f'{student_name}_{date_slug}')

    gdrive_backup = f'{os.path.basename(student_folder)}'
    gdrive_backup_path = os.path.join(gdrive_backup_transcription, gdrive_backup)

    os.makedirs(student_folder, exist_ok=True)

    transcript_unclean = read_file(transcript_path)
    pre_notes_unclean = read_file(pre_notes_path)

    transcript_clean, pre_notes_clean = clean_transcript(
        transcript_path=transcript_path,
        excel_path=pre_notes_path,
        student_name=student_name,
        tutor_name=tutor_name,
        debug=debug
    )

    if debug:
        print(f'Summarising tutorial with: {student_name}')
        print(f'Transcript: {transcript_clean}')
        print(f'Pre Notes: {pre_notes_clean}')

    with open(transcript_yml, 'r') as file:
        config = yaml.safe_load(file)

    user_message = config['user_message'].format(transcript_clean=transcript_clean, pre_notes_clean=pre_notes_clean, student=student_name)

    if debug:
        print(f"System Prompt: {config['system_prompt']}")
        print(f"User Message: {user_message}")

    chatbot_instance = Chatbot(openai_api_key, config['system_prompt'], model)

    if chat:
        chatbot_instance.chat(count_tokens=count_tokens)
    else:
        response, token_usage = chatbot_instance.chat(user_message, count_tokens=True) if count_tokens else (chatbot_instance.chat(user_message), None)
        print(f'Saved to {os.path.join(student_folder, student_name)}_summary.txt')
        print(response, token_usage)

        # Save response as text file with student name
        with open(os.path.join(student_folder, f'{student_name}_summary.txt'), 'w') as f:
            f.write(response)

        # Save cleaned text and summary as json file with student name
        data = {
            "cleaned_transcript": transcript_clean,
            "cleaned_pre_notes": pre_notes_clean,
            "summary": response
        }
        with open(os.path.join(student_folder, f'{student_name}.json'), 'w') as f:
            json.dump(data, f)

        # Save uncleaned transcript and pre-notes as json file with student name
        data_unclean = {
            "uncleaned_transcript": transcript_unclean,
            "uncleaned_pre_notes": pre_notes_unclean
        }
        with open(os.path.join(student_folder, f'{student_name}_unclean_data.json'), 'w') as f:
            json.dump(data_unclean, f)

        # Copy the original transcript file to the student's folder
        shutil.copy(transcript_path, os.path.join(student_folder, os.path.basename(transcript_path) + '_transcript'))

        # Copy the student folder to gdrive
        shutil.copytree(student_folder, gdrive_backup_path)   

