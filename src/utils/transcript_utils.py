import json

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
