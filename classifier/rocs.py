import numpy as np
import pylab as pl
import sys, types, pickle
from sklearn import svm, metrics
from Features import LDAFeatures, PCAFeatures
from utils import RGBIDataset, plot_classifier
from optparse import OptionParser
from Eval import *
from os.path import basename, splitext

###### MAIN ######
if __name__ == "__main__":
  """ Analyzes ROC curves for multiple saved models, sorts by label """
  # handle inputs
  parser = OptionParser()
  parser.add_option("-d", "--testData", action="store", type="string", dest="data", default="", help="Specify testing data file")
  parser.add_option("-m", "--model", action="store", type="string", dest="model", default="", help="Specify input model to plot/test (e.g. svc_rbf.svm)")
  (options, args) = parser.parse_args()

  if len(sys.argv) < 2:
    print "Usage: rocs testdata.txt model_glob"
    sys.exit(-1)
  
  #grab models
  dataFile = sys.argv[1]
  mFiles = sys.argv[2:]
  print mFiles

  # import some data to play with
  testing = RGBIDataset(dataFile, includeNull=True)
  Y = testing.target
  pixels = testing.pixels

  #grab ROC curve from each model
  for mFile in mFiles:

    #read model in - first is model object, second is feature object
    inFile = open(mFile, 'rb')
    model = pickle.load(inFile)
    reducer = pickle.load(inFile)

    #predict
    X = reducer.features(pixels)
    probs = np.array(model.predict_proba(X))
    Y_pred = probs.argmax(1)
    numClasses = probs.shape[1]

    # print accuracy
    for c in range(numClasses):
      correct = float(np.sum(Y_pred[Y==c]==c))
      num = float(np.sum(Y==c))
      print "Class %s (%d) accuracy: %f"%(testing.intToClass[c], c, correct/num)
    
    #compute ROC curve for each
    for c in range(numClasses):
      y_binary = np.ones(len(Y))
      y_binary[Y==c] = 2
      print y_binary
      scores = probs[:,c]
      fpr, tpr, thresholds = metrics.roc_curve(y_binary, scores)
      auc = metrics.auc(fpr, tpr)

      #label plot
      cleanName,ext = splitext(basename(mFile))
      lab = "%s auc: %f"%(cleanName, auc)
      
      #activate the correct subplot
      spNum = int("22%d"%(c+1))
      pl.subplot(spNum)
      pl.plot(fpr, tpr, label=lab)
      pl.title("ROCs for Label: %s"%(testing.intToClass[c]))
      pl.legend(loc=4)

  pl.show()
