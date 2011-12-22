from boxm2_scene_adaptor import *; 
from vil_adaptor import *;
from vpgl_adaptor import *;
import random, os, sys;  

#################################
# Set some update parameters
RGB = False; 
GPU = True;
REFINE_INTERVAL=5;
if len(sys.argv) > 1: 
  REFINE_MAX = int(sys.argv[1]);
else :
  REFINE_MAX = 250;
FILTER_MAX = 150; 
#################################

#should initialize a GPU
#scene_path = os.getcwd() + "/model/uscene.xml";
#scene = boxm2_scene_adaptor (scene_path, RGB, "gpu");  

uscene  = load_scene( os.getcwd() + "/model_scaled/uscene.xml"); 
uscene = scale_scene(uscene, .7); 

rscene  = load_scene( os.getcwd() + "/model_scaled/rscene.xml"); 
rscene = scale_scene(rscene, .7); 

save_scene(uscene, "uscene"); 
save_scene(rscene, "rscene"); 
  

## Get list of imgs and cams
#imgs_dir = os.getcwd() + "/nvm_out/imgs/"
#cams_dir = os.getcwd() + "/nvm_out/cams_krt/"
#imgs     = os.listdir(imgs_dir); imgs.sort();
#cams     = os.listdir(cams_dir); cams.sort();
#if len(imgs) != len(cams) :
#  print "CAMS NOT ONE TO ONE WITH IMAGES"
#  sys.exit();

################## 
## UPDATE LOOP
##################
#for x in range(0, 350, 1):

#  i = random.randint(0, len(imgs)-1); 
#  print "Iteration ", x, " Updating with frame ", imgs[i]; 
#  
#  #load image and camera
#  pcam        = load_camera(cams_dir+cams[i]); 
#  img, ni, nj = load_image (imgs_dir+imgs[i]); 

#	#render and save
#  expimg = scene.render(pcam, ni, nj);
#  bimg   = convert_image(expimg); 
#  exp_fname = os.getcwd() + "/exp_%(s)s.png"%{"s": imgs[i]};
#  save_image(bimg, exp_fname); 
#  
#  cd_img = scene.change_detect(pcam, img, expimg, 3, "raybelief"); 
#  cd_fname = os.getcwd() + "/change_%(s)s.tiff"%{"s": imgs[i]};
#  save_image(cd_img, cd_fname); 
	


