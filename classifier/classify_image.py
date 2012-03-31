import numpy as np
import pylab as pl
from sklearn import svm, datasets
from optparse import OptionParser
from PIL import Image
import transImage as ti

def classify_pixels(eoName, irName,reducer,model,dataset=None):
  eo = Image.open(eoName)
  ir = Image.open(irName)
  eoPix = np.float32(eo) / 255.0
  irPix = np.float32(ir) / 255.0

  eoDat = eoPix.reshape( (eoPix.shape[0]*eoPix.shape[1], eoPix.shape[2]) )
  eoDat = eoDat[:,:3]
  irDat = irPix.reshape( (irPix.shape[0]*irPix.shape[1], 1) )

  #reduce data
  data = reducer.features(eoDat, irDat)
  Z = np.array(model.predict(data))

  #print out classes
  if dataset:
    print "Num pixels classified: "
    for name,val in dataset.classMap.iteritems():
      print name, np.sum(Z==val)

  #shape
  Z = Z.reshape(irPix.shape)
  print "Image shape: ", Z.shape

  #try saving it out
  newImg = Image.fromarray(Z)
  newImg.save("test.tiff")

  return data, Z 
