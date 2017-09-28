import os
import sys
import time
import csv
from PIL import Image # $ pip install pillow
from os import listdir
from os.path import isfile, join
from collections import defaultdict

# Load libraries
import pandas
from pandas.tools.plotting import scatter_matrix
import matplotlib.pyplot as plt
from sklearn import model_selection
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
import numpy as np
import cv2
import imutils

from base import SingleInstance
from doxie import DoxieAutomator
import settings

class Trainer(SingleInstance):
    scanner_online = False

    LOCK_PATH = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "Trainer-lock")

    TRAIN_DATA_FOLDER = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "data", "train")
    TRAIN_FOLDER_BITMAPS = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "data", "train", "_photo")
    TRAIN_FOLDER_DOCS = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "data", "train", "_doc")

    TEST_FOLDER = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "data", "test")

    def initialize(self):
        self.log(u"Processing files to %s"%(settings.DOXIE_FOLDER))
        

    def loop(self):
        files = []

        image_files = self.get_latest_images(Trainer.TRAIN_FOLDER_BITMAPS)
        # print files
        files += self.prepare_and_store_images(image_files)

        doc_files = self.get_latest_images(Trainer.TRAIN_FOLDER_DOCS)
        # print files
        files += self.prepare_and_store_images(doc_files)

        train_filename = u'%s/%s'%(Trainer.TRAIN_DATA_FOLDER, 'train.csv')
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
        

    def prepare_and_store_images(self, files):

        # Determine bitmap or document
        # Determine orientation; auto rotate
        # Determine folder
        # Determine people in documents; suggest ordering
        # Determine grouping of files
        # Parse text and embed in file

        #FEATURES:
        #- total number of colors
        #- total number of lines / rectangles
        #- total number of words
        #- most frequent color

        output = []
        for image in files:
            
            # img = cv2.imread(image,0)
            # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            # cl1 = clahe.apply(img)

            # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # im_pil = Image.fromarray(img)

            im_pil = Image.open(image) #NOTE: it requires pillow 2.8+
            w, h = im_pil.size
            
            #Feature 1: Total number of colors:
            by_color = defaultdict(int)
            for pixel in im_pil.getdata():
                by_color[pixel] += 1
            total_unique_colors = len(by_color)

            #Feature 2: Total number of lines:

            # load the image and resize it to a smaller factor so that
            # the shapes can be approximated better
            cv_image = cv2.imread(image)
            resized = imutils.resize(cv_image, width=300)
            ratio = cv_image.shape[0] / float(resized.shape[0])
             
            # convert the resized image to grayscale, blur it slightly,
            # and threshold it
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (1, 1), 0)
            thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

            # find contours in the thresholded image and initialize the
            # shape detector
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if imutils.is_cv2() else cnts[1]

            #Find fine lines...
            edges = cv2.Canny(thresh.copy(), 100, 100 * (h/w))
            minLineLength = 100
            maxLineGap = 10
            lines = cv2.HoughLines(edges, 1, np.pi/180, 25)
            try:
                total_lines = len(lines)
            except:
                total_lines = 0
            

            #Most frequent color
            pixels = im_pil.getcolors(w * h)
            most_frequent_pixel = pixels[0]
            
            for count, colour in pixels:
                if count > most_frequent_pixel[0]:
                    most_frequent_pixel = (count, colour)
            red = most_frequent_pixel[1] if isinstance( most_frequent_pixel[1], int ) else most_frequent_pixel[1][0]
            green = most_frequent_pixel[1] if isinstance( most_frequent_pixel[1], int ) else most_frequent_pixel[1][1]
            blue = most_frequent_pixel[1] if isinstance( most_frequent_pixel[1], int ) else most_frequent_pixel[1][2]
            most_frequent_pixel_perceived_luminance = (0.299*red + 0.587*green + 0.114*blue)

            image_data = {
                'image':image,
                'total_contours':len(cnts),
                'total_unique_colors':total_unique_colors,
                # 'most_frequent_pixel':most_frequent_pixel[1],
                'total_lines':total_lines,
                'most_frequent_pixel_perceived_luminance':most_frequent_pixel_perceived_luminance,
                'is_doc':'_doc' in image
            }
            output.append(image_data)
            print image_data
        

        return output    


        # Spot Check Algorithms
        # models = []
        # models.append(('LR', LogisticRegression()))
        # models.append(('LDA', LinearDiscriminantAnalysis()))
        # models.append(('KNN', KNeighborsClassifier()))
        # models.append(('CART', DecisionTreeClassifier()))
        # models.append(('NB', GaussianNB()))
        # models.append(('SVM', SVC()))
        # # evaluate each model in turn
        # results = []
        # names = []
        # for name, model in models:
        #     kfold = model_selection.KFold(n_splits=10, random_state=seed)
        #     cv_results = model_selection.cross_val_score(model, X_train, Y_train, cv=kfold, scoring=scoring)
        #     results.append(cv_results)
        #     names.append(name)
        #     msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
        #     print(msg)