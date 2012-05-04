import numpy as np
import pylab as pl
from sklearn.decomposition import PCA
from sklearn.lda import LDA

"""
Feature transform classes (reducers).  Takes RGBI data and returns 
either reduced by LDA/PCA or just naive features.

Naive features are normalized pixel intensities and differences
"""

class LDAFeatures:
  def __init__(self, n_comp=3):
    self.lda = None
    self.n_comp = n_comp

  def features(self, pixels, gt=None):
    #grab feature stack
    fullFeatures = naive_features(pixels)
    print fullFeatures.shape

    #if the LDA from ground truth exists already, transform new features
    if gt==None and self.lda != None:
      print self.lda
      return self.lda.transform(fullFeatures)
    assert gt != None

    #otherwise, train LDA
    self.lda = LDA(n_components=self.n_comp).fit(fullFeatures,gt)
    print self.lda
    return self.lda.transform(fullFeatures)

class PCAFeatures:
  def __init__(self, n_comp=3):
    self.n_comp = n_comp

  def features(self, pixels):
    fullFeatures = naive_features(pixels)
    self.pca = PCA(n_components=self.n_comp).fit(fullFeatures)
    return self.pca.transform(fullFeatures)

class NaiveFeatures:
  def features(self, pixels):
    fullFeatures = naive_features(pixels)
    return fullFeatures


def naive_features(pixels):
  """Stacks a bunch of ratios/differences into a 
     high dimensional feature vector
  """
  #return pixels as only feature...
  if len(pixels.shape) == 1:
    return np.column_stack( (pixels,pixels) )

  #create sqr differences features for each channel
  intensity = pixels.sum(1) #total intensity
  pixelSize = pixels.shape[1]
  diffs = []
  for i in range(pixelSize):
    for j in range(pixelSize):
      if i==j: continue
      diff = (pixels[:,i] - pixels[:,j]) / intensity
      diffs.append(diff)
  diffs = np.array(diffs).T

  #create ratios
  ratios = []
  for i in range(pixelSize):
    ratio = pixels[:,i] / intensity
    ratios.append(ratio)
  ratios = np.array(ratios).T
  return np.column_stack( (pixels, ratios, diffs) )



