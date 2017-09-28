import os
import sys
import requests
import time

# Load libraries
from collections import defaultdict
from PIL import Image # $ pip install pillow
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


import json

from base import SingleInstance
import settings


class ImageIdentifier(SingleInstance):
    scanner_online = False

    LOCK_PATH = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "ImageIdentifier-lock")

    #FEATURES:
    #- total number of colors
    #- total number of lines / rectangles
    #- total number of words
    #- most frequent color
    def get_image_stats(self, image_path):
        
        im_pil = Image.open(image_path) #NOTE: it requires pillow 2.8+
        w, h = im_pil.size
        
        #Feature 1: Total number of colors:
        by_color = defaultdict(int)
        for pixel in im_pil.getdata():
            by_color[pixel] += 1
        total_unique_colors = len(by_color)

        #Feature 2: Total number of lines:

        # load the image and resize it to a smaller factor so that
        # the shapes can be approximated better
        cv_image = cv2.imread(image_path)
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

        try:
            red = most_frequent_pixel[1] if isinstance( most_frequent_pixel[1], int ) else most_frequent_pixel[1][0]
            green = most_frequent_pixel[1] if isinstance( most_frequent_pixel[1], int ) else most_frequent_pixel[1][1]
            blue = most_frequent_pixel[1] if isinstance( most_frequent_pixel[1], int ) else most_frequent_pixel[1][2]
            most_frequent_pixel_perceived_luminance = (0.299*red + 0.587*green + 0.114*blue)
        except:
            most_frequent_pixel_perceived_luminance = -1

        image_data = {
            'total_contours':len(cnts),
            'total_unique_colors':total_unique_colors,
            'total_lines':total_lines,
            'most_frequent_pixel_perceived_luminance':most_frequent_pixel_perceived_luminance
        }
        return image_data
