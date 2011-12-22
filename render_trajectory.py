from boxm2_scene_adaptor import *; 
from vil_adaptor import *;
from vpgl_adaptor import *;
import random, os, sys, scene_registry;  

####################################################### 
# handle inputs                                       #
#scene is given as first arg, figure out paths        #
scene_name = "apartments"                             #
if len(sys.argv) > 1 :                                #
  scene_name = sys.argv[1]                            #
scene_root = scene_registry.scene_root( scene_name ); #
#######################################################

#################################
# Set some update parameters
model_name = "model_color"
GPU = "gpu0";
NI=1280
NJ=720
#################################

#should initialize a GPU
os.chdir(scene_root);
scene_path = os.getcwd() + "/" + model_name + "/uscene.xml";
scene = boxm2_scene_adaptor(scene_path, GPU);  

#init trajectory 
startInc = 38.0; 
endInc = 38.0; 
radius   = 22.0; 
trajectory = init_trajectory(scene.scene, startInc, endInc, radius, NI, NJ);
trajDir = os.getcwd() + "/trajectory/"
if not os.path.exists(trajDir):
  os.mkdir(trajDir);

################# 
# UPDATE LOOP
#################
for x in range(0, 500, 1):

  #render frame
  prcam = trajectory_next(trajectory); 
  expimg = scene.render(prcam, NI, NJ);
  bimg   = convert_image(expimg); 
  exp_fname = trajDir + "/exp_%(#)03d.png"%{"#":x};
  save_image(bimg, exp_fname); 

#mencoder "mf://*.png" -mf fps=18 -o demo.avi -ovc lavc -lavcopts vcodec=msmpeg4v2:vbitrate=24000000

