from boxm2_scene_adaptor import *; 
from change.helpers import *;
import random, os, sys;  
from os.path import basename, splitext; 
import numpy
import pylab
from glob import glob; 


scene_type = "uscene"; #"uscene"; 
scene_path = "../model/" + scene_type + ".xml"; 
scene = boxm2_scene_adaptor(scene_path, False, "gpu"); 

#render all images, not just GT imgs
imgs = glob(os.getcwd() + "/imgs/*.png"); imgs.sort(); 
cams = glob(os.getcwd() + "/cams_krt/*.txt"); cams.sort(); 

#write depth images out
outdir = os.getcwd() + "/depths/" + scene_type + "/"; 
if not os.path.exists(outdir):
  os.makedirs(outdir); 

for idx, img in enumerate(imgs):
  #grab image number of ground truth image
  imgnum, ext  = os.path.splitext( basename(img) ); 
  cam          = load_perspective_camera(cams[idx]); 
  dimg, varimg = scene.render_depth(cam);
  save_image(dimg,   outdir + imgnum + ".tiff"); 
  save_image(varimg, outdir + imgnum + "_var.tiff"); 
