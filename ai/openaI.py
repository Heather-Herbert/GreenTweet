import logging
import datetime


class OpenaiClass:
    def __init__(self):
        self.logname = datetime.today().strftime('%Y-%m-%d')
        logging.basicConfig(filename=f'log/OpenAI-{self.logname}.log', level=logging.INFO,
                            format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def generate_comment(self, text):
        pass
