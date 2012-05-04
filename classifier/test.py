import numpy as np
import pylab as pl
import sys, random, types, pickle
from sklearn import svm, metrics
from Features import LDAFeatures, PCAFeatures
from utils import RGBIDataset, plot_classifier
from optparse import OptionParser
from Eval import *


###### MAIN ######
if __name__ == "__main__":
  
  # handle inputs
  parser = OptionParser()
  parser.add_option("-d", "--testData", action="store", type="string", dest="data", default="", help="Specify testing data file")
  parser.add_option("-m", "--model", action="store", type="string", dest="model", default="", help="Specify input model to plot/test (e.g. svc_rbf.svm)")
  parser.add_option("-v", "--visualize", action="store_true", dest="visualize", default=False, help="Visualize results of material classifier")
  (options, args) = parser.parse_args()

  # import some data to play with
  testing = RGBIDataset(options.data, includeNull=True)
  Y = testing.target
  pixels = testing.pixels

  #read model in - first is model object, second is feature object
  inFile = open(options.model, 'rb')
  model = pickle.load(inFile)
  reducer = pickle.load(inFile)
  pixelType = pickle.load(inFile)
  print "Testing on pixel type: ", pixelType

  #grab appropriate pixels
  if pixelType == "all":
    pixels = pixels
  elif pixelType == "EO":
    pixels = pixels[:,1:4]
  elif pixelType == "IR": 
    pixels = pixels[:,0]
  else:
    print "Unrecognized type %s !!!!"%pixelType
    sys.exit(-1)

  #reduce pixel features
  X = reducer.features(pixels)
  for c,v in testing.classMap.iteritems():
    print "%s (%d): %d items in training set"%(c,v,np.sum(Y==v))
 
  # PREDICT
  probs = np.array(model.predict_proba(X))
  numClasses = probs.shape[1]
  
  #visualize model if called for
  if options.visualize:
    y_graph = Y[testing.classes!="noclass"]
    x_graph = X[testing.classes!="noclass"]
    print "shapes: ", y_graph.shape, x_graph.shape
    plot_classifier(x_graph, y_graph, model, testing.classMap)

  #confusion matrix and accuracy
  Y_pred = probs.argmax(1)
  confMat = metrics.confusion_matrix(Y, Y_pred)
  printConfusionMatrix(confMat, testing.intToClass)
  
  #classification report?
  report = metrics.classification_report(Y, Y_pred, target_names=testing.intToClass)
  print report

  # print accuracy
  for c in range(numClasses):
    correct = float(np.sum(Y_pred[Y==c]==c))
    num = float(np.sum(Y==c))
    print "Class %s (%d) accuracy: %f"%(testing.intToClass[c], c, correct/num)

  #testing data from second image
  #compute ROC curve for each
  for c in range(numClasses):
    y_binary = np.ones(len(Y))
    y_binary[Y==c] = 2
    print y_binary
    scores = probs[:,c]
    fpr, tpr, thresholds = metrics.roc_curve(y_binary, scores)
    auc = metrics.auc(fpr, tpr)
    lab = "%s auc: %f"%(testing.intToClass[c], auc)
    pl.plot(fpr, tpr, label=lab)
  pl.legend()
  pl.show()


