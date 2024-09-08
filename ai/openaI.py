import logging
import datetime
from venv import logger

import requests
import json
import os
from dotenv import load_dotenv

class OpenaiClass:
    def __init__(self):
        self.logname = datetime.today().strftime('%Y-%m-%d')
        logging.basicConfig(filename=f'log/OpenAI-{self.logname}.log', level=logging.INFO,
                            format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        # Load the .env file
        load_dotenv()

    def generate_comment(self, text):

        url            = os.getenv('OPENAI_URL')
        model          = os.getenv('OPENAI_MODEL')
        system_content = os.getenv('OPENAI_SYSTEM')
        user_content   = (os.getenv('OPENAI_USER') or "") + "    " + text
        APITolken      = os.getenv('OPENAI_API_TOLKEN')

        # Prepare payload for ChatGPT API
        payload = {
            "model": f"{model}",
            "messages": [
                {
                    "role": "system",
                    "content": f"{system_content}"
                },
                {
                    "role": "user",
                    "content": f"{user_content}"
                }
            ]
        }

        # Prepare headers with bearer token
        headers = {
            "Authorization": f"Bearer {APITolken}",
            "Content-Type": "application/json"
        }

        # Make API request to ChatGPT
        response = requests.request("GET", url, headers=headers, data=payload)

        # Extract processed text from response
        try:
            processed_text = response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error("Error returned data from OpenAI")
            logger.error(response)
            raise Exception(f"Error returned data from OpenAI")

        return processed_text

