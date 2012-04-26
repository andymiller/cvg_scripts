import numpy as np
import pylab as pl
from PIL import Image
import random, types, pickle

class RGBIDataset:
  """ Load dataset from flat file - has data and target 
      NOTE: all classes are numbered in alphabetical order
            for consistency (noclass is always LAST)
  """
  def __init__(self, fname, includeNull=False):
    self.classes = []
    self.includeNull = includeNull
    self.load_flat_file(fname)

  def load_flat_file(self,fname):
    f = open(fname, 'r')
    pixels = []
    tempMap = {}  #temporary, unsorted class map
    for line in f:
      l = line.split()

      #only if classified
      datClass = l[0]
      if datClass == "noclass" and self.includeNull==False:
        continue

      #initialize class-int map (string to int)
      if not tempMap.has_key(datClass):
        tempMap[datClass] = len(tempMap)

      #keep track of string names, equivalent int, and float data
      self.classes.append( l[0] )
      pixels.append( [float(x) for x in l[1:]] );

    #alphabetize classes
    self.pixels = np.array(pixels)
    self.target = np.zeros(len(pixels))
    self.classes = np.array(self.classes)
    self.intToClass = []
    self.classMap = {}
    count = 0

    # sort keys, move "noclass" to end if applicable
    sortedKeys = sorted(tempMap.iterkeys())
    if "noclass" in sortedKeys:
      sortedKeys.remove("noclass")
      sortedKeys.append("noclass")
    for key in sortedKeys:
      self.target[self.classes==key] = count
      self.intToClass.append(key)
      self.classMap[key] = count
      count+=1
    #self.intToClass.append("noclass")
    print self.classMap
    print self.intToClass
    

def plot_classifier(X, Y, models, classMap=None):
  """ Plots classifier or classifiers on 2d plot """
  #handle single model
  if not isinstance(models, types.ListType):
    models = [models]
    titles = ["classifier"]
  else:
    titles = []
    for model in models:
      titles.append("Classifier...")
  
  #colors for different decisions
  colors = ["red", "green", "blue", "yellow", "black"]

  # create a mesh to plot in
  h = 50  # step size in mesh
  x_min, x_max = X[:, 0].min() - .002, X[:, 0].max() + .002
  y_min, y_max = X[:, 1].min() - .002, X[:, 1].max() + .002
  xx, yy = np.meshgrid(np.arange(x_min, x_max, (x_max-x_min)/h),
                       np.arange(y_min, y_max, (y_max-y_min)/h))
  
  #set cmap
  pl.set_cmap(pl.cm.Paired)
  for mi, clf in enumerate( models ):
    # Plot the decision boundary. For that, we will asign a color to each
    # point in the mesh [x_min, m_max]x[y_min, y_max].
    pl.subplot(1, len(models), mi + 1)
    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    pl.set_cmap(pl.cm.Paired)
    pl.contourf(xx, yy, Z)
    #pl.axis('off')

    # Plot also the training points
    if classMap:
      for c,i in classMap.iteritems():
        x = X[Y==i] 
        pl.plot(x[:,0], x[:,1], "o", c=colors[i], label=c) 

    #legend and title
    pl.legend()
    pl.title(titles[mi])
  pl.show()


def classify_pixels(eoName, irName, reducer, model, dataset=None):
  """ Creates and returns a PIL image with classes based on pixel values """ 
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
  X = reducer.features(pixels)

  print "classifying image ", eoName
  probs = np.array(model.predict_proba(X))
  Z = probs.argmax(1) #grab max value
  maxProbs = probs.max(1) #grab prob value for each max

  #shape
  Z = Z.reshape(irPix.shape).astype(float)
  newImg = Image.fromarray(Z)
  return X, Z, newImg 


