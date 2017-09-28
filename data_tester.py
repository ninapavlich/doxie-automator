import os
import sys
import time
import csv
from PIL import Image # $ pip install pillow
from os import listdir
from os.path import isfile, join
from collections import defaultdict
from datetime import datetime
import pickle
 

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

from doxieautomator.base import SingleInstance
from doxieautomator.image_identifier import ImageIdentifier
import doxieautomator.settings as settings

class TrainerDataTester(SingleInstance):
    scanner_online = False

    image_identifier = ImageIdentifier()

    LOCK_PATH = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "TrainerDataTester-lock")
    TRAIN_DATA_FOLDER = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "data", "train")
    TEST_FOLDER = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "data", "test")
    DATA_FOLDER = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "data")

    def initialize(self):
        self.log(u"Testing data in %s"%(TrainerDataTester.TRAIN_DATA_FOLDER))
        

    def loop(self):

        # Loading the saved decision tree model pickle
        decision_tree_pkl_filename = '%s/doc_type_classifier.pkl'%(TrainerDataTester.DATA_FOLDER)
        decision_tree_model_pkl = open(decision_tree_pkl_filename, 'rb')
        decision_tree_model = pickle.load(decision_tree_model_pkl)
        print "Loaded Decision tree model :: ", decision_tree_model

        test_files = self.get_latest_images(TrainerDataTester.TEST_FOLDER)
        # print files
        

        for image_path in test_files:
            print "Test %s"%(image_path)
            image_data = self.image_identifier.get_image_stats(image_path)
            print image_data
            result = decision_tree_model.predict([image_data.values()])
            print result

    def get_latest_images(self, folder):
        included_extensions = ['jpg', 'bmp', 'png', 'gif']
        return [u'%s/%s'%(folder, f) for f in listdir(folder) if any(f.lower().endswith(ext) for ext in included_extensions)]
        


if __name__ == "__main__":
    
    trainer = TrainerDataTester()
    trainer.loop()
    trainer.clean_up()        