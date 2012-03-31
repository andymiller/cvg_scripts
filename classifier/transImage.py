import numpy as np
import pylab as pl
from sklearn.decomposition import PCA
from sklearn.lda import LDA


class LDAFeatures:

  def __init__(self):
    self.lda = None

  def features(self, eoPixels, irPixels, gt=None):
    #grab feature stack
    fullFeatures = naive_features(eoPixels, irPixels)

    #if the LDA from ground truth exists already, transform new features
    if gt==None and self.lda != None:
      return self.lda.transform(fullFeatures)
    assert gt != None

    #otherwise, train LDA
    self.lda = LDA(n_components=2).fit(fullFeatures,gt)
    return self.lda.transform(fullFeatures)

class PCAFeatures:
  def features(self, eoPixels, irPixels):
    fullFeatures = naive_features(eoPixels, irPixels)
    self.pca = PCA(n_components=2).fit(fullFeatures)
    return self.pca.transform(fullFeatures)


def naive_features(eoPixels, irPixels):
  """Stacks a bunch of ratios/differences into a 
     high dimensional feature vector
  """
  #create sqr differences features for each channel
  allPix = np.column_stack( (eoPixels, irPixels) )
  intensity = np.sum(eoPixels[:,:3]) + irPixels[:,0] #total intensity
  diffs = []
  for i in range(4):
    for j in range(4):
      if i==j: continue
      diff = (allPix[:,i] - allPix[:,j]) / intensity
      diffs.append(diff)

  rRatio = pixelRatio(eoPixels, irPixels, "red")
  gRatio = pixelRatio(eoPixels, irPixels, "green")
  bRatio = pixelRatio(eoPixels, irPixels, "blue")
  iRatio = pixelRatio(eoPixels, irPixels, "ir")
  return np.column_stack( [rRatio, bRatio, gRatio, iRatio]+diffs )


def pixelRatio(eoPixels, irPixels, pixel_type="red"):
  """Green / (Green + Red + Blue + IR)"""
  assert eoPixels.shape[0] == irPixels.shape[0] 
  
  if pixel_type=="red":
    num = eoPixels[:,0]
  if pixel_type=="green":
    num = eoPixels[:,1]
  if pixel_type=="blue":
    num = eoPixels[:,2]
  if pixel_type=="ir":
    num = irPixels[:,0]

  denom = np.sum(eoPixels[:,:3]) + irPixels[:,0]
  return num / denom



