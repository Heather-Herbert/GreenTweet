import logging
import datetime

class TwitterClass:

    def __init__(self):
        self.logname = datetime.today().strftime('%Y-%m-%d')
        logging.basicConfig(filename=f'log/twitter-{self.logname}.log', level=logging.INFO, format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def send_msg(self):
        print("Message sent via Twitter")