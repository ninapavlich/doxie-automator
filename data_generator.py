import os
import sys
import time
import csv

from os import listdir
from os.path import isfile, join



from doxieautomator.base import SingleInstance
from doxieautomator.image_identifier import ImageIdentifier
import doxieautomator.settings as settings

class TrainerDataGenerator(SingleInstance):
    scanner_online = False

    image_identifier = ImageIdentifier()

    LOCK_PATH = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "TrainerDataGenerator-lock")

    TRAIN_DATA_FOLDER = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "data", "train")
    TRAIN_FOLDER_BITMAPS = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "data", "train", "_photo")
    TRAIN_FOLDER_DOCS = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "data", "train", "_doc")
    TRAIN_FOLDER_DRAWINGS = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "data", "train", "_drawing")
    TRAIN_FOLDER_GRAPHICS = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "data", "train", "_graphic")

    TEST_FOLDER = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "data", "test")

    def initialize(self):
        self.log(u"Generating image data from %s"%(TrainerDataGenerator.TRAIN_DATA_FOLDER))
        

    def loop(self):
        files = []

        image_files = self.get_latest_images(TrainerDataGenerator.TRAIN_FOLDER_BITMAPS)
        # print files
        files += self.prepare_and_store_images(image_files, 1)

        doc_files = self.get_latest_images(TrainerDataGenerator.TRAIN_FOLDER_DOCS)
        # print files
        files += self.prepare_and_store_images(doc_files, 2)

        drawings = self.get_latest_images(TrainerDataGenerator.TRAIN_FOLDER_DRAWINGS)
        # print files
        files += self.prepare_and_store_images(drawings, 3)

        graphics = self.get_latest_images(TrainerDataGenerator.TRAIN_FOLDER_GRAPHICS)
        # print files
        files += self.prepare_and_store_images(graphics, 4)

        train_filename = u'%s/%s'%(TrainerDataGenerator.TRAIN_DATA_FOLDER, 'train.csv')
        file_data = open(train_filename, 'w')
        csvwriter = csv.writer(file_data)
        count = 0
        for image_data_item in files:
              
              if count == 0:
                     header = image_data_item.keys()
                     csvwriter.writerow(header)
                     count += 1
              csvwriter.writerow(image_data_item.values())
        file_data.close() 

    def get_latest_images(self, folder):
        
        included_extensions = ['jpg', 'bmp', 'png', 'gif']
        return [u'%s/%s'%(folder, f) for f in listdir(folder) if any(f.lower().endswith(ext) for ext in included_extensions)]
        

    def prepare_and_store_images(self, files, image_type):

        # Determine bitmap or document
        # Determine orientation; auto rotate
        # Determine folder
        # Determine people in documents; suggest ordering
        # Determine grouping of files
        # Parse text and embed in file


        output = []
        for image_path in files[:20]:
            print image_path
            image_data = self.image_identifier.get_image_stats(image_path)

            image_data['type'] = image_type
            output.append(image_data)
            print image_data
        

        return output    


if __name__ == "__main__":
    
    trainer = TrainerDataGenerator()
    trainer.loop()
    trainer.clean_up()        