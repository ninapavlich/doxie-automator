import requests
import time
from requests.auth import HTTPBasicAuth
from PIL import Image # $ pip install pillow

import json

from doxieautomator import settings
from doxieautomator.doxie import DoxieAutomator
# from doxieautomator.pdf import PDFAutomator
from doxieautomator.train import Trainer



if __name__ == "__main__":
    import time

    doxie = DoxieAutomator()
    trainer = Trainer()
    try:
        if doxie.is_running:
            sys.exit("This app is already running!")
        
        # while True:
            # doxie.loop()
        trainer.loop()
            # time.sleep(5)

    finally:
        doxie.clean_up()
        trainer.clean_up()