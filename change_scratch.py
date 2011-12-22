#from boxm2_scene_adaptor import *; 
#from change.helpers import *;
#from os.path import basename, splitext; 
#from glob import glob; 
#import random, os, sys, numpy, pylab;  


from optparse import OptionParser

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename",
                  help="write report to FILE")
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

(options, args) = parser.parse_args()
print options
print args


#chImg,ni,nj = load_image("/home/acm/data/visualsfm/apts/change/change_imgs/results_model_fixed_/cd_1x1/cd_045841.tiff");
#for thresh in numpy.arange(.1, .9, .05): 
#    bimg = blob_change_detection( chImg, thresh)
#    save_image(bimg, "blob_" + str(thresh) + ".png");

