from boxm2_scene_adaptor import *; 
from change.helpers import *;
from os.path import basename, splitext; 
from glob import glob; 
import random, os, sys, numpy, pylab, scene_registry;  

chImg = load_image("/home/acm/data/visualsfm/apts/change/change_imgs/results_model_fixed_/cd_1x1/cd_045841.tiff");
for thresh in numpy.arange(.1, .9, .05): 
    bimg = blob_change_detection( chImg, thresh)
    save_image(bimg, "blob_" + str(thresh));
