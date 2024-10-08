import logging
from datetime import datetime
import os

import feedparser
from bs4 import BeautifulSoup
import requests
import unicodedata
import re

class RSSClass:

    def __init__(self):
        log_dir = 'log'
        logname = datetime.today().strftime('%Y-%m-%d')
        log_file = f'{log_dir}/rss-{logname}.log'

        # Create the directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Setup logging
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def get_most_popular_story(self, rss_url, processed_urls_file='processed_urls.txt'):
        # Fetch the RSS feed
        feed = feedparser.parse(rss_url)

        # Ensure the processed URLs file exists
        if not os.path.exists(processed_urls_file):
            with open(processed_urls_file, 'w') as f:
                pass  # Create the file if it doesn't exist

        # Load already processed URLs
        with open(processed_urls_file, 'r') as f:
            processed_urls = f.read().splitlines()

        # Iterate through feed entries to find a new URL
        for entry in feed.entries:
            story_url = entry.link

            # If the URL is not in the processed URLs list, save it and return it
            if story_url not in processed_urls:
                # Save the new URL to the processed file
                with open(processed_urls_file, 'a') as f:
                    f.write(story_url + '\n')

                return story_url

        # If no new story found, log the error and raise an exception
        self.logger.error(f'No new entries found in the RSS feed {rss_url}.')
        raise Exception("No new entries found in the RSS feed.")

    def get_article_text(self, article_url):
        # Fetch the webpage
        response = requests.get(article_url)
        if response.status_code == 200:
            # Parse the webpage content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract the main article text (simplified example)
            paragraphs = soup.find_all('p')
            article_text = ' '.join([p.get_text() for p in paragraphs])

            # Normalize the text (remove special characters and normalize unicode)
            article_text = unicodedata.normalize('NFKD', article_text)

            # Remove non-ASCII characters (optional, depends on your need)
            article_text = re.sub(r'[^\x00-\x7F]+', '', article_text)

            return article_text
        else:
            self.logger.error(f'No entries found in the RSS feed {article_url}.')
            raise Exception(f"Failed to retrieve the page: {response.status_code}")

    def get_article_image(self, article_url):
        response = requests.get(article_url)

        if response.status_code == 200:
            # Parse the webpage content with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Try to find the og:image meta tag
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                return og_image['content']

            # If no og:image, try to find the twitter:image meta tag
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image and twitter_image.get('content'):
                return twitter_image['content']

            # Extract images (we'll just take the first one as an example)
            images = soup.find_all('img')
            image_urls = [img['src'] for img in images if img.get('src')]
            if image_urls:
                return image_urls[0]

            # If no image is found
            self.logger.info('No images found in.')
            return None
        else:
            self.logger.error('error grabbing web page')
            raise Exception(f"Failed to retrieve the page: {response.status_code}")