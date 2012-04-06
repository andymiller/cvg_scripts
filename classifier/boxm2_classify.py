import numpy as np
import pylab as pl
import random, types, pickle
from sklearn import svm, datasets
from optparse import OptionParser
from PIL import Image
import classify_image as ci
import transImage as ti

class RGBIDataset:
  """ Load dataset from flat file - has data and target """
  def __init__(self, fname):
    self.classes = []
    self.target =[] 
    self.classMap = {}
    self.load_flat_file(fname)

  def load_flat_file(self,fname):
    f = open(fname, 'r')
    pixels = []
    for line in f:
      l = line.split()
      datClass = l[0]
      if datClass == "noclass": continue
      #if l[0]=="noclass" and random.random() > .5: continue

      #initialize class-int map (string to int)
      if not self.classMap.has_key(datClass):
        self.classMap[datClass] = len(self.classMap)

      #keep track of string names, equivalent int, and float data
      self.classes.append( l[0] )
      self.target.append( self.classMap[datClass] )
      pixels.append( [float(x) for x in l[1:]] );

    #numpy arrays
    self.classes = np.array(self.classes)
    self.target = np.array(self.target)
    self.pixels = np.array(pixels)
    
    #reverse class map (int to class)
    self.intToClass = dict((v,k) for k, v in self.classMap.iteritems())



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




###### MAIN ######
if __name__ == "__main__":
  # handle inputs
  parser = OptionParser()
  parser.add_option("-d", "--train", action="store", type="string", dest="data", default="/home/acm/Dropbox/cvg/MatClass/exp_002.txt", help="Specify training data file")
  parser.add_option("-t", "--test", action="store", type="string", dest="test", default="", help="Specify testing data file")
  parser.add_option("-s", "--save", action="store", type="string", dest="modelOut", default="", help="Specify model output file (e.g. svc_rbf.svm)")
  parser.add_option("-m", "--model", action="store", type="string", dest="modelIn", default="", help="Specify input model to plot/test (e.g. svc_rbf.svm)")
  (options, args) = parser.parse_args()
  print options

  # import some data to play with
  training = RGBIDataset(options.data)
  Y = training.target
  pixels = training.pixels
  print pixels


  #trasnform IR dataset to just take brightnes (total intensity), and ratios
  reducer = ti.LDAFeatures()
  X = reducer.features(pixels, Y)
 
  #print info
  print "Data shape: ", X.shape
  for c,v in training.classMap.iteritems():
    print c, ":", np.sum(Y==v), "items in training set"

  # we create an instance of SVM and fit out data. We do not scale our
  # data since we want to plot the support vectors
  if options.modelIn != "":
    print "Importing model!"
    inFile = open(options.modelIn, 'rb')
    rbf_svc = pickle.load(inFile)
    inFile.close()
  else:
    print "Learning SVM "
    rbf_svc = svm.SVC(kernel='rbf', gamma=0.7, probability=True).fit(X, Y)
    print "SVM Learned" 

  #write model out if specified
  if options.modelOut != "":
    print "saving model!"
    out = open(options.modelOut, 'wb')
    pickle.dump(rbf_svc, out)
    out.close()

  ########## TESTING ############
  #testing data from second image
  if options.test != "":
    testing = RGBIDataset(options.test)
    Y_test = testing.target
    X_test = reducer.features(testing.pixels)
    plot_classifier(X_test, Y_test, rbf_svc, testing.classMap)
   
 
  #plot on training data
  plot_classifier(X,Y,rbf_svc,training.classMap)

  #outside image stuff
  eoImg = "/home/acm/Dropbox/cvg/MatClass/Annotations/eoImgs/exp_000.png"
  irImg = "/home/acm/Dropbox/cvg/MatClass/Annotations/irImgs/exp_000.png"
  data, pixelZ = ci.classify_pixels(eoImg, irImg, reducer, rbf_svc, training); 
  #print "Pixel xmin, xmax, ", data[:,0].min(), data[:,0].max()
  #print "      ymin, ymax, ", data[:,1].min(), data[:,1].max()
  
  #DEBUG#####
  #eo = Image.open(eoImg)
  #ir = Image.open(irImg)
  #eoPix = np.float32(eo) / 255.0
  #irPix = np.float32(ir) / 255.0
  #eoDat = eoPix.reshape( (eoPix.shape[0]*eoPix.shape[1], eoPix.shape[2]) )
  #eoDat = eoDat[:,:3]
  #irDat = irPix.reshape( (irPix.shape[0]*irPix.shape[1], 1) )
  #pl.plot(imgs.eoPixels[:,0], imgs.eoPixels[:,1], "o", c="red", label="File") 
  #pl.plot(eoDat[:,0], eoDat[:,1], "x", c="blue", label="File")
  #pl.legend()
  #pl.show()



