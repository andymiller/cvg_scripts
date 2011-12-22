from boxm2_scene_adaptor import *; 
from vil_adaptor import *;
from vpgl_adaptor import *;
import numpy, random, os, sys, math, scene_registry;  

####################################################### 
# handle inputs                                       #
#scene is given as first arg, figure out paths        #
scene_name = "apartments"                             #
if len(sys.argv) > 1 :                                #
  scene_name = sys.argv[1]                            #
scene_root = scene_registry.scene_root( scene_name ); #
#######################################################

#################################################
# Set some update parameters
model_name = "model"
GPU = "gpu0"
NUM_IMAGES = 600
NI=1280
NJ=720

#ensure trajectory images can be written out
trajDir = os.getcwd() + "/spiral/"
if not os.path.exists(trajDir):
  os.mkdir(trajDir);
################################################

#should initialize a GPU
os.chdir(scene_root);
scene_path = os.getcwd() + "/" + model_name + "/uscene.xml";
scene = boxm2_scene_adaptor(scene_path, GPU);  
(sceneMin, sceneMax) = scene.bounding_box(); 

#init trajectory, look at center point - this can drift
startInc = 38.0; 
endInc   = 45.0; 
radius   = max(22.0, 1.4*(sceneMax[0]-sceneMin[0])); 
lookPt   = numpy.add(sceneMax, sceneMin)/2.0

########################################
#Generate cameras and render spiral
########################################
fLength = math.sqrt(NI*NI+NJ*NJ)
ppoint = (NI/2, NJ/2)
currR = radius
currInc = startInc
currAz = -90.0
dr = - (radius/1.45) / NUM_IMAGES
dAz = 1.0
dInc = (endInc-startInc)/NUM_IMAGES
for idx in range(NUM_IMAGES):

  #create cam, and render
  center = get_camera_center(currAz, currInc, currR, lookPt)
  cam = create_perspective_camera( (fLength,fLength), ppoint, center, lookPt )
  expimg = scene.render(cam, NI, NJ);
  bimg   = convert_image(expimg); 
  exp_fname = trajDir + "/exp_%(#)03d.png"%{"#":idx};
  save_image(bimg, exp_fname); 

  #increment az, incline and radius
  currR += dr
  currAz += dAz
  currInc += dInc

#mencoder "mf://*.png" -mf fps=18 -o demo.avi -ovc lavc -lavcopts vcodec=msmpeg4v2:vbitrate=24000000

