import numpy as np
import pylab as pl
from sklearn.decomposition import PCA
from sklearn.lda import LDA


class LDAFeatures:

  def __init__(self):
    self.lda = None

  def features(self, pixels, gt=None):
    #grab feature stack
    fullFeatures = naive_features(pixels)

    #if the LDA from ground truth exists already, transform new features
    if gt==None and self.lda != None:
      return self.lda.transform(fullFeatures)
    assert gt != None

    #otherwise, train LDA
    self.lda = LDA(n_components=2).fit(fullFeatures,gt)
    return self.lda.transform(fullFeatures)

class PCAFeatures:
  def features(self, pixels):
    fullFeatures = naive_features(pixels)
    self.pca = PCA(n_components=2).fit(fullFeatures)
    return self.pca.transform(fullFeatures)



def naive_features(pixels):
  """Stacks a bunch of ratios/differences into a 
     high dimensional feature vector
  """
  #create sqr differences features for each channel
  intensity = np.sum(pixels[:,0:4],1) #total intensity
  
  diffs = []
  for i in range(4):
    for j in range(4):
      if i==j: continue
      diff = (pixels[:,i] - pixels[:,j]) / intensity
      diffs.append(diff)

  ratios = []
  for i in range(4):
    ratio = pixels[:,i] / intensity
    ratios.append(ratio)
  return np.column_stack( ratios + diffs )



