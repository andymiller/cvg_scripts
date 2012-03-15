import numpy as np
import pylab as pl
import random
from sklearn import svm, datasets
from optparse import OptionParser
import classify_image as ci
import transImage as ti

class RGBIDataset:
  """ Load dataset from flat file - has data and target """
  def __init__(self, fname):
    self.classes = []
    self.data = []
    self.target =[] 
    self.classMap = {}
    self.numClass = 0
    self.load_flat_file(fname)

  def load_flat_file(self,fname):
    f = open(fname, 'r')
    eoPixels = []
    irPixels = []
    for line in f:
      l = line.split()
      if not(l[0] == "noclass" or l[0] == "trees"): continue      
      if l[0]=="noclass" and random.random() > .01: continue

      #initialize class int
      datClass = l[0]
      if not self.classMap.has_key(datClass):
        self.classMap[datClass] = self.numClass
        self.numClass += 1 

      #keep track of string names, equivalent int, and float data
      self.classes.append( l[0] )
      self.target.append( self.classMap[datClass] )
      irPixels.append( [float(l[1])] )
      eoPixels.append( [float(x) for x in l[2:]] );

    self.classes = np.array(self.classes)
    self.target = np.array(self.target)
    eoPixels = np.array(eoPixels)
    irPixels = np.array(irPixels)

    #trasnform IR dataset to just take brightnes (total intensity), and ratios
    self.data = ti.features(eoPixels, irPixels)
    print self.data.shape
    for c,v in self.classMap.iteritems():
      print c, ":", np.sum(self.target==v), "items in training set"

if __name__ == "__main__":
  # handle inputs
  parser = OptionParser()
  parser.add_option("-d", "--data", action="store", type="string", dest="data", default="/home/acm/Dropbox/cvg/MatClass/samples.txt",help="Specify data file")
  (options, args) = parser.parse_args()
  print options
  print args

  # import some data to play with
  #iris = datasets.load_iris()
  #X = iris.data[:, :2]  # we only take the first two features. We could
                        # avoid this ugly slicing by using a two-dim dataset
  #Y = iris.target
  imgs = RGBIDataset(options.data)
  X = imgs.data
  Y = imgs.target

  # we create an instance of SVM and fit out data. We do not scale our
  # data since we want to plot the support vectors
  svc = svm.SVC(kernel='rbf').fit(X, Y)

  eoImg = "/home/acm/Dropbox/cvg/MatClass/Annotations/eoImgs/exp_000.png"
  irImg = "/home/acm/Dropbox/cvg/MatClass/Annotations/irImgs/exp_000.png"
  #ci.classify_pixels(eoImg, irImg, svc, imgs); 

  rbf_svc = svm.SVC(kernel='rbf', gamma=0.7).fit(X, Y)
  poly_svc = svm.SVC(kernel='poly', degree=3).fit(X, Y)
  lin_svc = svm.LinearSVC().fit(X, Y)

  # create a mesh to plot in
  h = .002  # step size in the mesh
  x_min, x_max = X[:, 0].min() - .002, X[:, 0].max() + .002
  y_min, y_max = X[:, 1].min() - .002, X[:, 1].max() + .002
  xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                       np.arange(y_min, y_max, h))

  # title for the plots
  titles = ['SVC with linear kernel',
            'SVC with RBF kernel',
            'SVC with polynomial (degree 3) kernel',
            'LinearSVC (linear kernel)']
  pl.set_cmap(pl.cm.Paired)
  for i, clf in enumerate((svc, rbf_svc, poly_svc, lin_svc)):
     # Plot the decision boundary. For that, we will asign a color to each
     # point in the mesh [x_min, m_max]x[y_min, y_max].
      pl.subplot(2, 2, i + 1)
      Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])

     # Put the result into a color plot
      Z = Z.reshape(xx.shape)
      pl.set_cmap(pl.cm.Paired)
      pl.contourf(xx, yy, Z)
      pl.axis('off')

     # Plot also the training points
      pl.scatter(X[:, 0], X[:, 1], c=Y)

      pl.title(titles[i])

  pl.show()


