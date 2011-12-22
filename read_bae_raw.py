from vil_adaptor import *
from bbas_adaptor import *
import os, sys
import struct
from PIL import Image
import array
from os.path import basename, splitext; 
import random, os, sys, numpy, pylab;  

###########################################
#check args
###########################################
if len(sys.argv) < 2:
  print "First argument should be raw file!"
  sys.exit(-1)
rawFile = sys.argv[1]; 
INTERVAL= 70

##open input file
rawName, ext = splitext(basename(rawFile))
#rawName = "/media/Data/" + rawName
#print rawName
#if not os.path.exists(rawName) :
#  os.mkdir(rawName)
  
stream, numImgs = bae_raw_stream(rawFile)
for idx in range(0, numImgs, INTERVAL):
  print "grabbing image ", idx, " of ",  numImgs
  img,time = seek_frame(stream, idx)
  imgName = "ir_%05d_time_%010d.tiff" % (idx, time)
  save_image(img, imgName)
  remove_from_db(img)

