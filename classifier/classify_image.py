import numpy as np
import pylab as pl
from sklearn import svm, datasets
from optparse import OptionParser
from PIL import Image
import transImage as ti

def classify_pixels(eoName, irName, reducer, model, dataset=None):
  
  #grab pixel values from images
  eo = Image.open(eoName)
  ir = Image.open(irName)
  eoPix = np.float32(eo) / 255.0
  irPix = np.float32(ir) / 255.0
  eoDat = eoPix.reshape( (eoPix.shape[0]*eoPix.shape[1], eoPix.shape[2]) )
  eoDat = eoDat[:,:3]
  irDat = irPix.reshape( (irPix.shape[0]*irPix.shape[1], 1) )

  #zip pixels into (IR, R, G, B) intensities
  pixels = np.column_stack( (irDat, eoDat) )

  #reduce data
  print "dim reducing features"
  X = reducer.features(pixels)
  #X = X[:,:100]

  #print "classifying image"
  #Z = np.array(model.predict(X))
  print "Predicting probabilities"
  probs = np.array(model.predict_proba(X))
  Z = probs.argmax(1) #grab max value
  maxProbs = probs.max(1) #grab prob value for each max
  Z[maxProbs < .9] = -1

  #print out classes
  if dataset:
    print "Num pixels classified: "
    for name,val in dataset.classMap.iteritems():
      print val, name, np.sum(Z==val)

  #shape
  Z = Z.reshape(irPix.shape).astype(float)
  print "Image shape: ", Z.shape

  #try saving it out
  newImg = Image.fromarray(Z)
  newImg.save("test.tiff")

  return X, Z 
