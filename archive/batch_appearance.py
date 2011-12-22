from boxm2_scene_adaptor import *; 
from vil_adaptor import *;
from vpgl_adaptor import *;
import random, os, sys;  
from glob import glob; 

#################################
# Set some update parameters
RGB = False; 
GPU = True;
#################################

#should initialize a GPU
scene_path = os.getcwd() + "/model_batch/uscene.xml";
scene = boxm2_scene_adaptor (scene_path, RGB, "gpu1");  

# Get list of imgs and cams
imgs_dir = os.getcwd() + "/nvm_out/imgs/"
cams_dir = os.getcwd() + "/nvm_out/cams_krt/"
imgs = glob(imgs_dir + "/*.png"); imgs.sort(); 
cams = glob(cams_dir + "/*.txt"); cams.sort(); 
if len(imgs) != len(cams) :
  print "CAMS NOT ONE TO ONE WITH IMAGES"
  sys.exit();

#for idx in range(0, len(imgs)) :

#  print '--------------------------';
#  print "processing image " + imgs[idx];
#  
#  #load cam/img
#  img, ni, nj = load_image (imgs_dir+imgs[idx]);
#  pcam        = load_perspective_camera(cams_dir+cams[idx]); 
#  gcam        = persp2gen(pcam,ni,nj); 
# 
#  # update aux per view call
#  fname, fextension = splitext(imgs[idx]); 
#  imageID = basename(fname)
#  scene.update_aux(img, gcam, imageID); 
# write the entire cache 
#scene.write_cache(); 

#write aux data 
#scene.write_aux_data(imgs, cams) 
 
#batch update 
scene.batch_paint(imgs, cams);


