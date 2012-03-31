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
parser.add_option("-b", "--buildImgs", action="store", type="string", dest="buildImgs", default="nvm_out", help="Specify location of build images, default=nvm_out")
parser.add_option("-p", "--passes", action="store", type="int", dest="passes", default=2, help="number of passes over dataset")
parser.add_option("-r", "--refineoff", action="store_true", dest="norefine", default=False, help="turn refine off")
parser.add_option("-m", "--mask", action="store", type="string", dest="mask", default="", help="mask file path")
parser.add_option("-c", "--buildchange", action="store_true", dest="buildchange", default=False, help="build change images?")
parser.add_option("-i", "--imgtype", action="store", type="string", dest="itype", default="png", help="specify image type (tif, png, tiff, TIF)")
parser.add_option("-v", "--variance", action="store", type="float", dest="var", default="-1.0", help="Specify fixed mog3 variance, otherwise learn it")
parser.add_option("-d", "--downSamp", action="store", type="float", dest="downSamp", default="1.0", help="Specify if images/cams should be downsampled before updating")
parser.add_option("-n", "--numSkip", action="store", type="int", dest="skip", default=1, help="Specify how many images to use in each pass (1=every, 2=every other...)")
parser.add_option("-a", "--render", action="store_true", dest="render", default=False, help="Render images from update viewpoints")
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
REFINE_INTERVAL=10
REFINE_ON = not options.norefine
BUILD_CHANGE_IMGS = options.buildchange
MASK_FILE = options.mask
#################################

#should initialize a GPU
os.chdir(scene_root)
scene_path = os.getcwd() + "/" + SCENE_NAME
if not os.path.exists(scene_path):
  print "SCENE NOT FOUND! ", scene_path
  sys.exit(-1)
scene = boxm2_scene_adaptor (scene_path, GPU);  

# Get list of imgs and cams
train_imgs = os.getcwd() + "/" + options.buildImgs + "/imgs/*." + options.itype
train_cams = os.getcwd() + "/" + options.buildImgs + "/cams_krt/*.txt"
imgs = glob(train_imgs)
cams = glob(train_cams)
if BUILD_CHANGE_IMGS and os.path.exists(os.getcwd() + "/change/imgs/") and os.path.exists(os.getcwd() + "/change/cams_krt/"):
  change_imgs = os.getcwd() + "/change/imgs/*." + options.itype
  change_cams = os.getcwd() + "/change/cams_krt/*.txt"
  imgs += glob(change_imgs)
  cams += glob(change_cams)
imgs.sort()
cams.sort()
if len(imgs) != len(cams) :
  print "CAMS NOT ONE TO ONE WITH IMAGES"
  print "CAMS: ", len(cams), "  IMGS: ", len(imgs)
  sys.exit();
  
#mask image
if MASK_FILE=="":
  mask = None 
else: 
  print "loading maskfile"
  mask = load_image(MASK_FILE);

#write cache, delete appearance,    
#move_appearance( os.getcwd() + "/model/"); 

#repeat 5 passes over the image set
for p in range(0,NUMPASSES):

  #update using every image once
  frames = range(0,len(imgs))[::options.skip]; 
  random.shuffle(frames); 
  for idx, i in enumerate(frames): 
    print "Pass: ", p, ", Iteration ", idx, " of ", len(frames)
    
    #load image and camera
    pcam        = load_perspective_camera(cams[i]); 
    img, ni, nj = load_image (imgs[i]); 

    if options.downSamp != 1.0:
      dni, dnj = options.downSamp*ni, options.downSamp*nj
      dimg = resize(img, dni, dnj, "byte")
      dcam = resample_perspective_camera(pcam, (ni,nj), (dni,dnj))
      remove_from_db([img, pcam])
      img = dimg
      pcam = dcam
      ni,nj = dni, dnj

    #update call
    scene.update(pcam, img, True, mask, "",  options.var); 

    if options.render:
      rimg = scene.render(pcam, ni, nj)
      save_image(rimg, "update_%i.tiff"%(idx))

    #refine
    if idx%REFINE_INTERVAL==0 and REFINE_ON:
      scene.refine();

    #filter
    # if x%20==0 and x < FILTER_MAX:
    # scene.median_filter()
    
    #clean up
    remove_from_db([img, pcam])
    if idx%10==9:
      scene.write_cache();
   
scene.write_cache(); 

