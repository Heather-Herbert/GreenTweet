import logging
import datetime
import feedparser
from bs4 import BeautifulSoup
import requests


class RSSClass:

    def __init__(self):
        self.logname = datetime.today().strftime('%Y-%m-%d')
        logging.basicConfig(filename=f'rss/main-{self.logname}.log', level=logging.INFO, format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def get_most_popular_story(self, rss_url):
        # Set application up

        # Fetch the RSS feed
        feed = feedparser.parse(rss_url)

        # Assume the first entry is the most popular story
        if feed.entries:
            return feed.entries[0].link  # return the link of the most popular story
        else:
            self.logger.error(f'No entries found in the RSS feed {rss_url}.')
            raise Exception("No entries found in the RSS feed.")

    def get_article_text(self, article_url):
        # Fetch the webpage
        response = requests.get(article_url)
        if response.status_code == 200:
            # Parse the webpage content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract the main article text (simplified example)
            paragraphs = soup.find_all('p')
            article_text = ' '.join([p.get_text() for p in paragraphs])

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