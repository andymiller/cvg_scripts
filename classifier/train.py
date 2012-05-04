import numpy as np
import pylab as pl
import  pickle, os
from sklearn import svm, datasets
from optparse import OptionParser
from utils import RGBIDataset, plot_classifier
import Features
from Features import LDAFeatures, PCAFeatures, NaiveFeatures
from LogReg import LogReg
from MultiLogReg import MultiLogReg
from MultiSVM import MultiSVM

if __name__ == "__main__":
  # handle inputs
  parser = OptionParser()
  parser.add_option("-d", "--data", action="store", type="string", dest="data", default="", help="Specify training data file (flatfile generated from boxm2 classify)")
  parser.add_option("-s", "--save", action="store", type="string", dest="modelOut", default="", help="Specify model output file (e.g. svc_rbf.svm)")
  parser.add_option("-m", "--modelType", action="store", type="string", dest="modelType", default="svm_lda", help="Specify type of model to learn")
  parser.add_option("-v", "--visualize", action="store_true", dest="visualize", default=False, help="Visualize results of material classifier")
  parser.add_option("-c", "--complexity", action="store", type="int", dest="complexity", default=2, help="Specify dimensionality of reduced data set (for lda/pca models)")
  parser.add_option("-p", "--pixels", action="store", type="string", dest="pixels", default="all", help="Specify which pixels to use, EO, IR, or all")
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
  if options.pixels == "all":
    pixels = training.pixels
  elif options.pixels == "EO":
    pixels = training.pixels[:,1:4]
  elif options.pixels == "IR": 
    pixels = training.pixels[:,0]
  for c,v in training.classMap.iteritems():
    print c, ":", np.sum(Y==v), "items in training set"

  #Train classifiers
  print "Learning ",options.modelType
  if options.modelType=="svm_lda":
    reducer = LDAFeatures(n_comp=options.complexity) #reduces features (using LDA)
    X = reducer.features(pixels, Y) #creates features
    model = svm.SVC(kernel='rbf', gamma=0.7, probability=True).fit(X, Y)
  if options.modelType=="svm_pca":
    reducer = PCAFeatures(n_comp=self.complexity)
    X = reducer.features(pixels)
    model = svm.SVC(kernel="rbf", gamma=0.7, probability=True).fit(X,Y)
  
  #Independent svm models
  if options.modelType=="isvm":
    reducer = NaiveFeatures()
    X = reducer.features(pixels)
    model = MultiSVM()
    model.fit(X,Y)
  if options.modelType=="isvm_lda":
    reducer = LDAFeatures(n_comp=options.complexity)
    X = reducer.features(pixels, Y)
    model = MultiSVM()
    model.fit(X,Y)
  if options.modelType=="isvm_pca":
    reducer = PCAFeatures(n_comp=options.complexity)
    X = reducer.features(pixels)
    model = MultiSVM()
    model.fit(X,Y)  
  
  #Logistic Regression
  if options.modelType=="ilogreg":
    reducer = NaiveFeatures()
    X = reducer.features(pixels)
    model = MultiLogReg()
    model.fit(X,Y)
  if options.modelType=="ilogreg_lda":
    reducer = LDAFeatures(n_comp=options.complexity)
    X = reducer.features(pixels, Y) 
    model = MultiLogReg()
    model.fit(X,Y)

  #write model out if specified
  print "Model learned: %s"%model
  print "saving model as ", options.modelOut
  out = open(options.modelOut, 'wb')
  pickle.dump(model, out)
  pickle.dump(reducer, out)
  pickle.dump(options.pixels, out)
  out.close()

  #visualize model if called for
  if options.visualize:
    plot_classifier(X,Y,model,training.classMap)

