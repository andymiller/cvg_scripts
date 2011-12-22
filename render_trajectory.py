from boxm2_scene_adaptor import *; 
from vil_adaptor import *;
from vpgl_adaptor import *;
import random, os, sys, scene_registry;  
from optparse import OptionParser

####################################################### 
# handle inputs                                       #
#scene is given as first arg, figure out paths        #
parser = OptionParser()
parser.add_option("-s", "--scene", action="store", type="string", dest="scene", help="specify scene name")
parser.add_option("-x", "--xmlfile", action="store", type="string", dest="xml", default="uscene.xml", help="scene.xml file name (model/uscene.xml, model_fixed/scene.xml, rscene.xml)")
parser.add_option("-g", "--gpu",   action="store", type="string", dest="gpu",   default="gpu1", help="specify gpu (gpu0, gpu1, etc)")
parser.add_option("-m", "--maxFrames", action="store", type="int", dest="maxFrames", default=500, help="max number of frames to render")
(options, args) = parser.parse_args()
print options
print args

scene_root = scene_registry.scene_root( options.scene ); #
model_name = options.xml
if not os.path.exists(scene_root + "/" + model_name):
  print "Cannot find file: ", scene_root+"/"+model_name
  sys.exit(-1) 
GPU = options.gpu;
MAX_FRAMES = options.maxFrames
NI=1280
NJ=720
#################################

#should initialize a GPU
os.chdir(scene_root);
scene_path = os.getcwd() + "/" + model_name;
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
for x in range(0, MAX_FRAMES, 1):

  #render frame
  prcam = trajectory_next(trajectory); 
  expimg = scene.render(prcam, NI, NJ);
  bimg   = convert_image(expimg); 
  exp_fname = trajDir + "/exp_%(#)03d.png"%{"#":x};
  save_image(bimg, exp_fname); 

#mencoder "mf://*.png" -mf fps=18 -o demo.avi -ovc lavc -lavcopts vcodec=msmpeg4v2:vbitrate=24000000

