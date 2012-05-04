import numpy as np
import pylab as pl
from PIL import Image
import os, sys, pickle
from glob import glob
from utils import classify_pixels

#### MAIN: classifies pixels for input image ########
if __name__ == "__main__":
  if len(sys.argv) < 4: 
    print "Usage: classifyPixels.py model.svm imageEO imageIR"
    sys.exit(-1)

  # grab args
  modelFile = sys.argv[1]
  eoName = sys.argv[2]
  irName = sys.argv[3]

  # make image list
  if os.path.isdir(eoName) and os.path.isdir(irName):
    print "classifying every image in dataset"
    eoFiles = glob.glob(eoName + "/*.png")
    irFiles = glob.glob(irName + "/*.png")
    assert len(eoFiles) == len(irFiles)
  else: 
    eoFiles = [eoName]
    irFiles = [irName]

  # load model 
  inFile = open(modelFile, 'rb')
  model = pickle.load(inFile)
  reducer = pickle.load(inFile)

  #establish colors: 
  colors = ["gray", "green", "teal", "black"]

  # runo n each file
  for idx in range(len(eoFiles)):
    img = classify_pixels(eoFiles[idx], irFiles[idx], reducer, model, colors); 
    img.save("class_img_%d.png"%idx )

