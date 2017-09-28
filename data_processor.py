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

from doxieautomator.base import SingleInstance
from doxieautomator.doxie import DoxieAutomator
import doxieautomator.settings as settings

class TrainerDataProcessor(SingleInstance):
    scanner_online = False

    LOCK_PATH = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "TrainerDataProcessor-lock")
    TRAIN_DATA_FOLDER = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "data", "train")
    TEST_FOLDER = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "data", "test")

    def initialize(self):
        self.log(u"Processing data in %s"%(TrainerDataProcessor.TRAIN_DATA_FOLDER))
        

    def loop(self):
        train_filename = u'%s/%s'%(TrainerDataProcessor.TRAIN_DATA_FOLDER, 'train.csv')

        dataset = pandas.read_csv(train_filename)
        print(dataset.shape)
        print(dataset.head(20))
        print(dataset.describe())    
        print(dataset.groupby('is_doc').size())

        # box and whisker plots
        dataset.plot(kind='box', subplots=True, layout=(5,2), sharex=False, sharey=False)
        plt.show()

        # histograms
        dataset.hist()
        plt.show()

        # scatter plot matrix
        scatter_matrix(dataset)
        plt.show()

        # Split-out validation dataset
        array = dataset.values
        X = array[:,1:]
        Y = array[:,0:1]
        validation_size = 0.20
        seed = 7
        X_train, X_validation, Y_train, Y_validation = model_selection.train_test_split(X, Y, test_size=validation_size, random_state=seed)

        # Test options and evaluation metric
        seed = 7
        scoring = 'accuracy'

        # Spot Check Algorithms
        models = []
        models.append(('LR', LogisticRegression()))
        models.append(('LDA', LinearDiscriminantAnalysis()))
        models.append(('KNN', KNeighborsClassifier()))
        models.append(('CART', DecisionTreeClassifier()))
        models.append(('NB', GaussianNB()))
        models.append(('SVM', SVC()))
        # evaluate each model in turn
        results = []
        names = []
        for name, model in models:
            kfold = model_selection.KFold(n_splits=10, random_state=seed)
            cv_results = model_selection.cross_val_score(model, X_train, Y_train, cv=kfold, scoring=scoring)
            results.append(cv_results)
            names.append(name)
            msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
            print(msg)

        # Compare Algorithms
        fig = plt.figure()
        fig.suptitle('Algorithm Comparison')
        ax = fig.add_subplot(111)
        plt.boxplot(results)
        ax.set_xticklabels(names)
        plt.show()
        


        # Make predictions on validation dataset
        print "LogisticRegression model:"
        lr = LogisticRegression()
        lr.fit(X_train, Y_train)
        predictions = lr.predict(X_validation)
        print(accuracy_score(Y_validation, predictions))
        print(confusion_matrix(Y_validation, predictions))
        print(classification_report(Y_validation, predictions))

        print "DecisionTreeClassifier model:"
        cart = DecisionTreeClassifier()
        cart.fit(X_train, Y_train)
        predictions = cart.predict(X_validation)
        print(accuracy_score(Y_validation, predictions))
        print(confusion_matrix(Y_validation, predictions))
        print(classification_report(Y_validation, predictions))


if __name__ == "__main__":
    
    trainer = TrainerDataProcessor()
    trainer.loop()
    trainer.clean_up()        