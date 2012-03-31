import random, os, sys, scene_registry;  
from boxm2_scene_adaptor import *; 
from vil_adaptor import *;
from vpgl_adaptor import *;
from bbas_adaptor import *;
from change.helpers import *
from glob import glob
from optparse import OptionParser

####################################################### 
# handle inputs                                       #
#scene is given as first arg, figure out paths        #
parser = OptionParser()
parser.add_option("-s", "--scene", action="store", type="string", dest="scene", help="specify scene name")
parser.add_option("-x", "--xmlfile", action="store", type="string", dest="xml", default="uscene.xml", help="scene.xml file name (model/uscene.xml, model_fixed/scene.xml, rscene.xml)")
parser.add_option("-g", "--gpu",   action="store", type="string", dest="gpu",   default="gpu1", help="specify gpu (gpu0, gpu1, etc)")
parser.add_option("-p", "--passes", action="store", type="int", dest="passes", default=2, help="number of passes over dataset")
#parser.add_option("-m", "--mask", action="store", type="string", dest="mask", default="", help="mask file path")
parser.add_option("-i", "--imgtype", action="store", type="string", dest="itype", default="png", help="specify image type (tif, png, tiff, TIF)")
parser.add_option("-l", "--imgLoc", action="store", type="string", dest="imgLoc", default="nvm_out", help="specify location of image, camera directory")
parser.add_option("-n", "--numskip", action="store", type="int", dest="skip", default=1, help="Specify which images to use (1=all, 2=every other, ect)")
(options, args) = parser.parse_args()
print options
print args

# handle inputs
#scene is given as first arg, figure out paths
scene_root = scene_registry.scene_root( options.scene ); 

# Set some update parameters
SCENE_NAME = options.xml
GPU = options.gpu
NUMPASSES = options.passes;    #num passes over the dataset
#################################

#should initialize a GPU
os.chdir(scene_root)
scene_path = os.getcwd() + "/" + SCENE_NAME
if not os.path.exists(scene_path):
  print "SCENE NOT FOUND! ", scene_path
  sys.exit(-1)
scene = boxm2_scene_adaptor (scene_path, GPU);  

# Get list of imgs and cams
train_imgs = os.getcwd() + "/" + options.imgLoc + "/imgs/*." + options.itype
train_cams = os.getcwd() + "/" + options.imgLoc + "/cams_krt/*.txt"
imgs = glob(train_imgs)
cams = glob(train_cams)
imgs.sort()
cams.sort()
if len(imgs) != len(cams) :
  print "CAMS NOT ONE TO ONE WITH IMAGES"
  print "CAMS: ", len(cams), "  IMGS: ", len(imgs)
  sys.exit();
  
#paint by passing over the dataset
for p in range(0,NUMPASSES):

  #update using every image once
  frames = range(0,len(imgs))[::options.skip]; 
  random.shuffle(frames); 
  for idx, i in enumerate(frames): 
    print "Pass: ", p, ", Iteration ", idx, " of ", len(frames)
    
    #load image and camera
    pcam        = load_perspective_camera(cams[i]); 
    img, ni, nj = load_image (imgs[i]); 

    #update call
    scene.update_app(pcam, img);
    
    #clean up
    remove_from_db([img, pcam])

    #write cache every 10 updates
    if idx%10==0:
      scene.write_cache()

  #write cache after each pass
  scene.write_cache();
   


