import cleantext
from nltk.corpus import stopwords
import pandas as pd
import numpy as np


class TranscriptCleaner:
    def __init__(self, transcript_path, excel_path=None, student_name=None, tutor_name="Keir Williams", debug=False):
        self.transcript_path = transcript_path
        self.excel_path = excel_path
        self.student_name = student_name
        self.tutor_name = tutor_name
        self.debug = debug
        self.custom_stopwords = set(stopwords.words('english') + ['uh', 'um', 'hmm', 'yeah', 'okay'])

    def clean_transcript_text(self, text):
        tutor_initials = "".join(name[0] for name in self.tutor_name.split())
        text = text.replace(self.tutor_name, tutor_initials)
        text = cleantext.clean(
            text,
            extra_spaces=True,
            stemming=True,
            stopwords=True,
            lowercase=True,
            numbers=True,
            punct=True,
            stp_lang='english'
        )
        cleaned_text = ' '.join(word for word in text.split() if word not in self.custom_stopwords)
        return cleaned_text

    def clean_notes_text(self, text):
        # If the object is a date, format it as a string
        if isinstance(text, pd.Timestamp) or isinstance(text, np.datetime64):
            text = str(pd.to_datetime(str(text)).date())

        text = cleantext.clean(
            text,
            extra_spaces=True,  # Remove extra white spaces
            stemming=True,  # Do not stem the words
            stopwords=False,  # Do not remove stop words
            lowercase=True,  # Convert to lowercase
            numbers=True,  # Remove all digits
            punct=True,  # Remove all punctuations
            stp_lang='english'  # Language for stop words
        )

        return text



    def clean_transcript(self):
        try:
            with open(self.transcript_path, 'r', encoding='ISO-8859-1') as file:
                text = file.read()
            return self.clean_transcript_text(text)
        except Exception as e:
            if self.debug:
                print(f"An error occurred: {str(e)}")
            return None

    def get_student_data(self):
        try:
            df = pd.read_excel(self.excel_path)
            df.columns = ['ID', 'Start time', 'Completion time', 'Email', 'Name',
                          'Last modified time', 'Date of Tutorial', 'Tutorial Aims',
                          'Questions / Discussion points', 'Materials to consider']
            student_row = df[df['Name'] == self.student_name]
            return student_row
        except Exception as e:
            if self.debug:
                print(f"An error occurred while extracting student data: {str(e)}")
            return None

    def clean_pre_tutorial_notes(self):
        try:
            student_row = self.get_student_data()
            key_columns = ['Name', 'Date of Tutorial', 'Tutorial Aims', 'Questions / Discussion points']
            cleaned_data = {col: self.clean_notes_text(student_row[col].values[0]) for col in key_columns}

            # Format cleaned data into sentences
            formatted_text = (f"Student {cleaned_data['Name']} had a tutorial on {cleaned_data['Date of Tutorial']}. "
                              f"The aims of the tutorial included: {cleaned_data['Tutorial Aims']}. "
                              f"Discussion points were as follows: {cleaned_data['Questions / Discussion points']}.")

            return formatted_text

        except Exception as e:
            if self.debug:
                print(f"An error occurred while extracting pre-tutorial notes: {str(e)}")
            return None

