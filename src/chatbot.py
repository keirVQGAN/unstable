import openai
import tiktoken
import json
from pathlib import Path
import logging

class Chatbot:
    COST_PER_TOKEN = {'gpt-3.5-turbo': 0.004, 'gpt-4': 0.03}

    def __init__(self, openai_key, system_prompt=None, model="gpt-4", encoding="cl100k_base", chat_history_path='chat_history.json', debug=False):
        self.system_prompt = system_prompt
        self.model = model
        self.encoding = encoding
        self.messages = self.load_system_prompt()
        self.encoder = tiktoken.get_encoding(self.encoding)
        self.chat_history_path = Path(chat_history_path)
        openai.api_key = openai_key
        self.debug = debug

        if self.debug:
            logging.basicConfig(filename='chatbot.log', level=logging.DEBUG)

    def load_system_prompt(self):
        return [{"role": "system", "content": self.system_prompt}] if self.system_prompt else []

    def get_prompt(self, user_input):
        return self.messages + [{"role": "user", "content": user_input}]

    def add_chat_completion(self, user_input):
        try:
            completion = openai.ChatCompletion.create(
                model=self.model,
                messages=self.get_prompt(user_input),
            )
            self.messages.append({"role": "assistant", "content": completion.choices[0].message.content})
            return completion.choices[0].message.content
        except Exception as e:
            if self.debug:
                logging.error(f"Error creating chat completion: {str(e)}")
            raise

    @property
    def used_tokens(self):
        token_count = len(self.encoder.encode(" ".join([msg["content"] for msg in self.messages])))
        token_cost = self.calculate_token_cost(token_count)
        return token_count, token_cost

    def calculate_token_cost(self, token_count):
        cost_per_token = self.COST_PER_TOKEN.get(self.model, 0)
        return token_count / 1000 * cost_per_token

    def save_chat_history(self):
        try:
            self.chat_history_path.write_text(json.dumps(self.messages, indent=4))
            print(f"Conversation history saved as '{self.chat_history_path}'.")
        except Exception as e:
            if self.debug:
                logging.error(f"Error saving chat history: {str(e)}")
            raise

    def chat(self, user_message=None, count_tokens=False):
        try:
            return self.interactive_chat(count_tokens) if user_message is None else self.non_interactive_chat(user_message, count_tokens)
        except Exception as e:
            if self.debug:
                logging.error(f"Error in chat method: {str(e)}")
            raise

    def interactive_chat(self, count_tokens):
        while True:
            user_input = input("You: ")

            if user_input.lower() in ('**end', '**save'):
                if user_input.lower() == '**end':
                    print("End of the chat.")
                    return self.messages
                self.save_chat_history()
                continue

            completion = self.add_chat_completion(user_input)
            print("Bot:", completion)
            if count_tokens:
                token_count, token_cost = self.used_tokens
                print(f"Used Tokens: {token_count} ({token_cost:.6f} USD)")

    def non_interactive_chat(self, user_message, count_tokens):
        completion = self.add_chat_completion(user_message)
        if count_tokens:
            token_count, token_cost = self.used_tokens
            return completion, (token_count, f"{token_cost:.6f}")
        return completion
