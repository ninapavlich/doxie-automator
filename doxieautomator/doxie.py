import os
import sys
import time
import json
import cStringIO
import logging

import requests
from requests.auth import HTTPBasicAuth
from PIL import Image


from base import SingleInstance
import settings


class DoxieAutomator(SingleInstance):
    scanner_online = False

    DELETE_ON_CORRUPTED = True #If true, delete a file that has an IO error. This happens when the file on the doxie is corrupted.

    LOCK_PATH = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "DoxieAutomator-lock")

    _observers = []

    def initialize(self):
        self.log(u"Looking for Doxie on %s"%(settings.DOXIE_SERVER))
        self._observers = []
        self.loop()


    def loop(self):
        files = self._get_latest_images()
        status = self._prepare_and_store_images(files)

    def bind_to(self, callback):
        self._observers.append(callback)
    
    def _get_all_scans_url(self):
        return u'%s/scans.json'%(settings.DOXIE_SERVER)

    def _get_latest_images(self):
        
        
        try:
            if settings.DOXIE_USERNAME and settings.DOXIE_PASSWORD:
                r = requests.get(self._get_all_scans_url(), auth=(settings.DOXIE_USERNAME, settings.DOXIE_PASSWORD))
            else:
                r = requests.get(self._get_all_scans_url())
        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            self.log(u'Timeout trying to connect to %s'%(self._get_all_scans_url()))
            return []
        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            self.log(u'Too many redirect when trying to connect to %s'%(self._get_all_scans_url()))
            return []
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            self.log(u'Error when trying to connect to %s: %s'%(self._get_all_scans_url(), str(e)))
            return []
            
        
        try:
            scans_json = json.loads( r.text )

            if self.scanner_online == False:
                self.log(u"Doxie online")
            self.scanner_online = True
            
            if len(scans_json) > 0:
                self.log(u"Detected %s new scans"%(len(scans_json)))

        except ValueError, e:
            scans_json = None

            if self.scanner_online == True:
                self.log("Doxie offline")
            self.scanner_online = False
        
        if scans_json:
            return [ u'%s/scans%s'%(settings.DOXIE_SERVER, scan["name"]) for scan in scans_json]
            

        return []

    def _prepare_and_store_images(self, files):

        counter = 1
        for file in files:

            filename = self._process_filename(file, 'pdf', counter, len(files))
            image = self._retrieve_image(file)

            retrieve_successful = False
            try:
                retrieve_successful, local_filename = self._store_file(filename, image)
                
            except IOError as e:
                self.log(u"I/O error({0}) on {1}: {2}".format(e.errno, filename, e.strerror))

            if retrieve_successful == True or DoxieAutomator.DELETE_ON_CORRUPTED:
                self._delete_original(file)
            else:
                self.log(u"Skipping deleting file %s since retrieval was not successful"%(filename))

            if retrieve_successful:
                for callback in self._observers:
                    callback(local_filename)

            counter += 1


    def _retrieve_image(self, url):
        self.log('Retrieving %s from Doxie'%(url))
        if settings.DOXIE_USERNAME and settings.DOXIE_PASSWORD:
            r = requests.get(url, auth=(settings.DOXIE_USERNAME, settings.DOXIE_PASSWORD), stream=True)
        else:
            r = requests.get(url, stream=True)

        r.raw.decode_content = True

        #If the image file on Doxie is .PDF, PIL doesn't process it properly.
        #A workaround is to dump the http request content into a cStriongIO,
        #the advantage is that it can be reused without having to make
        #another requests to Doxie. This way if errors are thrown we can try
        #again with a different method.

        csi = cStringIO.StringIO()
        csi.write(r.raw.read())
        csi.seek(0)#rewind
        try:
            im = Image.open(csi)
        except IOError:
            self.log('%s not a .jpg file. Probably a .pdf file.'%(url))
            csi.seek(0)#rewind
            return csi
        return im

    

    def _process_filename(self, filename, filetype, counter, total):
        timestr = time.strftime("%Y-%m-%d_%H-%M-%S")

        if total > 1:
            return u'%s-%s.%s'%(timestr, counter, filetype)
        return u'%s.%s'%(timestr, filetype)

    def _store_file(self, filename, image):

        timestr = time.strftime("%Y-%m-%d")
        doxie_file_folder = u'%s/%s'%(settings.DOXIE_FOLDER, timestr)
        

        if not os.path.exists(doxie_file_folder):
            os.makedirs(doxie_file_folder)
        
        image_path = u'%s/%s'%(doxie_file_folder, filename)
        self.log('Saving new scan to %s'%(image_path))
        
        # At this point image is either a PIL.Image, or just a raw
        # IO object
        
        try:
            image.convert('RGB').save(image_path, "PDF", Quality = 100)
        except AttributeError:
            image.seek(0)#rewind
            with open(image_path,'w') as destination:
                destination.write(image.read())

        return (True, image_path)

    def _delete_original(self, original):

        self.log('Clearing %s from Doxie.'%(original))
        r = requests.delete(original)
        