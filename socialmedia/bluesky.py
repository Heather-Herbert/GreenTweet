import logging
import datetime


class BlueskyClass:
    def __init__(self):
        self.logname = datetime.today().strftime('%Y-%m-%d')
        logging.basicConfig(filename=f'log/bluesky-{self.logname}.log', level=logging.INFO,
                            format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def upload_image(self, image):
        pass

    def send_message(self, text, image):
        pass

    def login(self, username, password):
        pass
