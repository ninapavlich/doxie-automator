import time

from doxieautomator.doxie import DoxieAutomator

if __name__ == "__main__":
    import time

    doxie = DoxieAutomator()
    
    try:
        if doxie.is_running:
            sys.exit("This app is already running!")
        
        while True:
            doxie.loop()
            time.sleep(30)

    finally:
        doxie.clean_up()