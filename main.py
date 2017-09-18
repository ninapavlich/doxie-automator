import urllib2, base64
import json

from base import SingleInstance
import settings

class DoxieAutomator(SingleInstance):
    def loop(self):
        
        files = self.get_latest_images()
        print files
        cleaned_files = self.prepare_images(files)

    
    def get_all_scans_url(self):
        return u'%s/scans.json'%(settings.DOXIE_SERVER)

    def get_latest_images(self):
        print self.get_all_scans_url()
        
        request = urllib2.Request( self.get_all_scans_url() )
        if settings.DOXIE_USERNAME and settings.DOXIE_PASSWORD:
            base64string = base64.b64encode('%s:%s' % (settings.DOXIE_USERNAME, settings.DOXIE_PASSWORD))
            request.add_header("Authorization", "Basic %s" % base64string)   
        f = urllib2.urlopen(request)
        
        try:
            scans_json = json.loads( f.read() )
        except ValueError, e:
            scans_json = None
        
        if scans_json:
            return [ u'%s/scans%s'%(settings.DOXIE_SERVER, scan["name"]) for scan in scans_json]
            

        return []

    def prepare_images(self, files):
        return files

    def upload_images(self, images):
        print 'upload imges'
        print images




if __name__ == "__main__":
    import time

    si = DoxieAutomator()
    try:
        if si.is_running:
            sys.exit("This app is already running!")
        
        while True:
            si.loop()
            time.sleep(5)

    finally:
        si.clean_up()