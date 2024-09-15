import requests

from ai.openaI import OpenaiClass
from socialmedia.bluesky import BlueskyClass
from web.rss import RSSClass

import os
import logging
from datetime import datetime




def main():
    # Set application up
    log_dir = 'log'
    logname = datetime.today().strftime('%Y-%m-%d')
    log_file = f'{log_dir}/main-{logname}.log'

    # Create the directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    # Setup logging
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

    logging.info('Set-up logging')
    BlueSky_instance = BlueskyClass()
    BlueSky_instance.login()

    # Get URL
    rss_instance = RSSClass()
    LateistStory = rss_instance.get_most_popular_story('https://feeds.bbci.co.uk/news/uk/rss.xml')
    logging.info(f"Laterst story is {LateistStory}")

    # Get Text and Image of article
    StoryText = rss_instance.get_article_text(LateistStory)
    ImageURL = rss_instance.get_article_image(LateistStory)
    logging.info(f"Laterst story Image is {ImageURL}")

    # Build reply
    AI_instance = OpenaiClass()
    reply = AI_instance.generate_comment(StoryText)
    ImageID = ''

    response = requests.get(ImageURL)

    # Check if the request was successful
    if response.status_code == 200:
        # Get the binary content of the image
        image_data = response.content
        logging.error("Image downloaded successfully!")
        ImageID = BlueSky_instance.upload_image(image_data, ImageURL)
    else:
        logging.error(f"Failed to download image. Status code: {response.status_code}")

    # Send an HTTP GET request to the image URL
    BlueSky_instance.send_message(reply,LateistStory,ImageID,'')


    # Tidy up

if __name__ == "__main__":
    main()