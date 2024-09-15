import logging
import re
from datetime import datetime
import mimetypes
from venv import logger
import requests
import json
import os
from dotenv import load_dotenv
from markdown_it.rules_inline import image


class BlueskyClass:
    def __init__(self):
        log_dir = 'log'
        logname = datetime.today().strftime('%Y-%m-%d')
        log_file = f'{log_dir}/BlueSky-{logname}.log'

        # Create the directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Setup logging
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        # Load the .env file
        load_dotenv()

    def upload_image(self, image, imageFileName):
        # Guess the MIME type based on the file extension
        self.mime_type, _ = mimetypes.guess_type(imageFileName)

        # If the MIME type is unknown, you can default to 'application/octet-stream'
        if self.mime_type is None:
            self.mime_type = 'application/octet-stream'

        self.logger.info('Uploading image')

        # Define the URL and headers
        url = "https://bsky.social/xrpc/com.atproto.repo.uploadBlob"
        headers = {
            'Accept-Encoding': 'application/json; charset=utf-8',
            'Content-Type': self.mime_type,  # Set the guessed MIME type
            'Authorization': f'Bearer {self.accessJwt}'
        }

        # Send the POST request
        response = requests.post(url, headers=headers, data=image)

        self.size = 0
        try:
            # Extract the '$link' value
            link = response.json()['blob']['ref']['$link']
            self.size = response.json()['blob']['size']
            return link
        except KeyError as e:
            print(f"KeyError: Missing key in response JSON - {e}")
            return None

    def send_message(self, text, url, image=None, alttext=''):
        # Generate the current time in the required format
        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        # Create the record content
        record_content = {
            "$type": "app.bsky.feed.post",
            "text": f"{text} {url}",
            "createdAt": current_time
        }

        # Prepare the facets list
        facets = []

        # Convert text to bytes (UTF-8 encoding) for accurate byte indexing
        text_bytes = text.encode('utf-8')

        # Helper function to convert character index to byte index
        def char_to_byte_index(char_index):
            return len(text[:char_index].encode('utf-8'))

        # Find and handle hashtags with correct byte positions for UTF-8
        hashtags = [(m.start(), m.end(), m.group()[1:]) for m in re.finditer(r'#\w+', text)]
        for start, end, tag in hashtags:
            byte_start = char_to_byte_index(start)
            byte_end = char_to_byte_index(end)
            facets.append({
                "index": {
                    "byteStart": byte_start,
                    "byteEnd": byte_end
                },
                "features": [
                    {
                        "$type": "app.bsky.richtext.facet#tag",
                        "tag": tag
                    }
                ]
            })

        # Handle embedded images
        if image:
            record_content["embed"] = {
                "$type": "app.bsky.embed.images",
                "images": [
                    {
                        "alt": alttext,
                        "image": {
                            "$type": "blob",
                            "ref": {
                                "$link": image
                            },
                            "mimeType": self.mime_type,
                            "size": self.size
                        },
                    }
                ]
            }

        # Handle the link as a facet with correct byte indexing
        url_start_byte = len(text_bytes) + 1  # After the text
        facets.append({
            "index": {
                "byteStart": url_start_byte,
                "byteEnd": url_start_byte + len(url.encode('utf-8'))
            },
            "features": [
                {
                    "$type": "app.bsky.richtext.facet#link",
                    "uri": url
                }
            ]
        })

        # Add facets to the record content if any
        if facets:
            record_content["facets"] = facets

        # Prepare the payload
        payload = {
            "repo": self.did,
            "collection": "app.bsky.feed.post",
            "record": record_content
        }

        # Set up headers
        headers = {
            "Accept-Encoding": "application/json; charset=utf-8",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.accessJwt}"
        }

        # Get the host from environment variables
        host = os.getenv('BLUESKY_HOST')
        target_url = f"{host}com.atproto.repo.createRecord"

        # Send the request
        response = requests.post(target_url, headers=headers, json=payload)

        return response

    def login(self):

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
