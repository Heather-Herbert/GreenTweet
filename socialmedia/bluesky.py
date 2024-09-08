import logging
import datetime
import mimetypes
from venv import logger
import requests
import json
import os
from dotenv import load_dotenv


class BlueskyClass:
    def __init__(self):
        self.logname = datetime.today().strftime('%Y-%m-%d')
        logging.basicConfig(filename=f'log/BlueSky-{self.logname}.log', level=logging.INFO,
                            format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        # Load the .env file
        load_dotenv()

    def upload_image(self, image):
        # Guess the MIME type based on the file extension
        mime_type, _ = mimetypes.guess_type(image)

        # If the MIME type is unknown, you can default to 'application/octet-stream'
        if mime_type is None:
            mime_type = 'application/octet-stream'

        # Read the file data
        with open(image, 'rb') as file:
            payload = file.read()

        # Define the URL and headers
        url = "https://bsky.social/xrpc/com.atproto.repo.uploadBlob"
        headers = {
            'Accept-Encoding': 'application/json; charset=utf-8',
            'Content-Type': mime_type,  # Set the guessed MIME type
            'Authorization': self.accessJwt,
        }

        # Send the POST request
        response = requests.post(url, headers=headers, data=payload)

        self.image = ''

    def send_message(self, text, url, image, alttext):

        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        post_content = {
            "text": f"{text} {url}",  # Combine text and URL in the post body
            "createdAt": current_time  # Replace with current time
        }

        # If there's an image, add the image reference to the post content
        if image:
            post_content["embed"] = {
                "images": [
                    {
                        "image": self.image,  # Image blob reference
                        "alt": alttext  # Alternative text for accessibility
                    }
                ]
            }


        payload = json.dumps({
            "repo": f"{self.did}",
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "record": post_content
            }
        })


        pass

    def login(self, username, password):

        host     = os.getenv('BLUESKY_HOST')
        handle   = os.getenv('BLUESKY_HANDLE')
        password = os.getenv('BLUESKY_PASSWORD')

        url = f"{host}com.atproto.server.createSession"

        payload = json.dumps({
            "identifier": f"{handle}",
            "password": f"{password}"
        })

        headers = {
            'Accept-Encoding': 'application/json; charset=utf-8',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        try:
            # Load JSON data
            json_obj = json.loads(response.text)

            # Check if 'accessJwt' exists and return it
            if 'accessJwt' in json_obj:
                self.accessJwt = json_obj['accessJwt']
                self.did       = json_obj['did']
                return
            else:
                raise KeyError("accessJwt not found in JSON data.")

        except KeyError as e:
            logger.error(f"Error: {str(e)}")
            raise  # Re-raise the error after logging it
