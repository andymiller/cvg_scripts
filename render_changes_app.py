from boxm2_scene_adaptor import *; 
from boxm2_change_roc import *
from vil_adaptor import *
from vpgl_adaptor import *
import os, sys;  
from os.path import basename, splitext; 
import numpy
import pylab
from glob import glob; 
from change.helpers import *

#################################
# Set some update parameters
GPU = True;
RGB = False;
#################################

#load up opencl scene
scene_path = "../model/rscene.xml";  
scene = boxm2_scene_adaptor(scene_path, RGB, "gpu");  

## move the apperance out the way
move_appearance( os.getcwd() + "/../model/"); 

#grab all change images
allImgs = glob(os.getcwd() + "/imgs/*.png"); allImgs.sort(); 
allCams = glob(os.getcwd() + "/cams_krt/*.txt"); allCams.sort(); 

#load up GT images, grab the corresponding imgs and cams
#gts = glob(os.getcwd() + "/gt/*.png"); gts.sort(); 
#imgs = []; cams = []
for idx, img in enumerate(allImgs): 
  imgnum, ext = os.path.splitext( basename(img) ); 
  #bname = imgnum.split("_"); 
  cimg = os.getcwd() + "/imgs/" + imgnum + ".png"; 
  ccam = os.getcwd() + "/cams_krt/" + imgnum + "_cam.txt"; 
  
  #find image in list, update w/ two previous, two next
  currIdx = idx;
  for i in range(currIdx-2, currIdx+2) :
    if i<0 or i>=len(allImgs) or i==currIdx: continue
    pcam        = load_perspective_camera(allCams[i]); 
    img, ni, nj = load_image (allImgs[i]); 
    scene.update(pcam, img, False);  #false=dont update alpha
  
  n=5; 
  outdir = os.getcwd() + "/results_app/cd_%(#)dx%(#)d/"%{"#":n}; 
  render_changes(scene, cimg, ccam, outdir, n, "raybelief"); 
  
  #clear those last 4 updates
  scene.clear_cache(); 
    
# move appearance back
return_appearance( os.getcwd() + "/../model/"); 



