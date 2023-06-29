import yaml
import json
import os
from src.chatbot import Chatbot
from src.transcript_cleaner import TranscriptCleaner

def clean_transcript(transcript_path, excel_path, student_name, tutor_name, json_file_path, debug=True):
    # Instantiate the TranscriptCleaner class
    transcript_cleaner = TranscriptCleaner(
        transcript_path=transcript_path,
        excel_path=excel_path,
        student_name=student_name,
        tutor_name=tutor_name,
        debug=debug
    )

    # Call the clean_transcript method
    transcript_clean = transcript_cleaner.clean_transcript()

    # Call the clean_pre_tutorial_notes method
    pre_notes_clean = transcript_cleaner.clean_pre_tutorial_notes()

    # Save the cleaned transcript and pre-tutorial notes to a JSON file
    data = {
        "transcript_clean": transcript_clean,
        "pre_notes_clean": pre_notes_clean
    }

    with open(json_file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

    return transcript_clean, pre_notes_clean



def transcript(transcript_path, pre_notes_path, json_file_path, openai_api_key, model='gpt-4', count_tokens=False, chat=False, debug=False, tutor_name='Keir Williams'):
    # Extracting student's name from the transcript file name
    student_name = os.path.basename(transcript_path).replace('.txt', '')

    transcript_clean, pre_notes_clean = clean_transcript(
        transcript_path=transcript_path,
        excel_path=pre_notes_path,
        student_name=student_name,
        tutor_name=tutor_name,
        json_file_path=json_file_path,
        debug=debug
    )

    if debug:
        print(f'Summarising tutorial with: {student_name}')
        print(f'Transcript: {transcript_clean}')
        print(f'Pre Notes: {pre_notes_clean}')

    with open('./config/transcript/config_transcript.yml', 'r') as file:
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
        print(f'Saved to {student_name}_summary.txt')
        print()
        print(response, token_usage)

        # Save response as text file with student name
        with open(f'{student_name}_summary.txt', 'w') as f:
            f.write(response)


        # Save cleaned text and summary as json file with student name
        data = {
            "cleaned_transcript": transcript_clean,
            "cleaned_pre_notes": pre_notes_clean,
            "summary": response
        }
        with open(f'{student_name}.json', 'w') as f:
            json.dump(data, f)
