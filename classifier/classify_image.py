import numpy as np
import pylab as pl
from sklearn import svm, datasets
from optparse import OptionParser
from PIL import Image
import transImage as ti

def classify_pixels(eoName, irName, model, dataset):
  eo = Image.open(eoName)
  ir = Image.open(irName)
  eoPix = np.float32(eo) / 255.0
  irPix = np.float32(ir) / 255.0

  eoDat = eoPix.reshape( (eoPix.shape[0]*eoPix.shape[1], eoPix.shape[2]) )
  irDat = irPix.reshape( (irPix.shape[0]*irPix.shape[1], 1) )
  data = ti.features(eoDat, irDat)
  Z = np.array(model.predict(data))

  #print out classes
  print "Num pixels classified: "
  for name,val in dataset.classMap.iteritems():
    print name, np.sum(Z==val)

  Z = Z.reshape(irPix.shape)
  print Z.shape

  #try saving it out
  newImg = Image.fromarray(Z)
  newImg.save("test.tiff")
