import numpy as np
import pylab as pl
import  pickle, os
from sklearn import svm, datasets
from optparse import OptionParser
from utils import RGBIDataset, plot_classifier
import Features
from Features import LDAFeatures, PCAFeatures
from LogReg import LogReg
from MultiSVM import MultiSVM

if __name__ == "__main__":
  # handle inputs
  parser = OptionParser()
  parser.add_option("-d", "--data", action="store", type="string", dest="data", default="", help="Specify training data file (flatfile generated from boxm2 classify)")
  parser.add_option("-s", "--save", action="store", type="string", dest="modelOut", default="", help="Specify model output file (e.g. svc_rbf.svm)")
  parser.add_option("-m", "--modelType", action="store", type="string", dest="modelType", default="svm_lda", help="Specify type of model to learn")
  parser.add_option("-v", "--visualize", action="store_true", dest="visualize", default=False, help="Visualize results of material classifier")
  (options, args) = parser.parse_args()
  print options

  # verify args
  if not os.path.exists(options.data):
    print "No data file!" 
    sys.exit(-1)
  if options.modelOut == "":
    print "No output model file!"
    sys.exit(-1)

  # import raw training data
  training = RGBIDataset(options.data)
  Y = training.target
  pixels = training.pixels
  for c,v in training.classMap.iteritems():
    print c, ":", np.sum(Y==v), "items in training set"

  #Train classifiers
  print "Learning ",options.modelType
  if options.modelType=="svm_lda":
    reducer = LDAFeatures() #reduces features (using LDA)
    X = reducer.features(pixels, Y) #creates features
    model = svm.SVC(kernel='rbf', gamma=0.7, probability=True).fit(X, Y)
  if options.modelType=="svm_pca":
    reducer = PCAFeatures()
    X = reducer.features(pixels)
    model = svm.SVC(kernel="rbf", gamma=0.7, probability=True).fit(X,Y)
  if options.modelType=="logreg":
    print "Log reg not yet implemented"
    #X = Features.naive_features(pixels)
    #Y[Y!=0] = -1
    #Y[Y==0] = 1
    #model = LogReg()
    #model.fit(X,Y)
    #Yt = model.predict(X)
    #correct = np.sum(Y==Yt)
    #print "Accuracy: ", float(correct)/len(Y)
  if options.modelType=="isvm" or options.modelType=="isvm_lda":
    reducer = LDAFeatures()
    X = reducer.features(pixels, Y)
    model = MultiSVM()
    model.fit(X,Y)
  print "Model learned: %s"%model

  #write model out if specified
  print "saving model as ", options.modelOut
  out = open(options.modelOut, 'wb')
  pickle.dump(model, out)
  pickle.dump(reducer, out)
  out.close()

  #visualize model if called for
  if options.visualize:
    plot_classifier(X,Y,rbf_svc,training.classMap)

