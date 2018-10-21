import time
import logging

from doxieautomator.doxie import DoxieAutomator

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s %(module)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)-8s [%(process)d] %(message)s')


def notify_new_file(local_filename):
    logging.info("New file downloaded from Doxie to: %s"%(local_filename))


if __name__ == "__main__":
    import time

    doxie = DoxieAutomator()
    doxie.bind_to(notify_new_file)

    try:
        if doxie.is_running:
            sys.exit("This app is already running!")
        
        while True:
            doxie.loop()
            time.sleep(30)

    finally:
        doxie.stop()