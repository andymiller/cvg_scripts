from boxm2_scene_adaptor import *; 
from change.helpers import *;
from os.path import basename, splitext; 
from glob import glob; 
import random, os, sys, numpy, pylab, scene_registry
from optparse import OptionParser

####################################################### 
# handle inputs                                       #
#scene is given as first arg, figure out paths        #
parser = OptionParser()
parser.add_option("-s", "--scene", action="store", type="string", dest="scene", help="specify scene name")
parser.add_option("-x", "--xmlfile", action="store", type="string", dest="xml", default="model/uscene.xml",help="model/scene name (eg model/uscene.xml))")
parser.add_option("-t", "--type",  action="store", type="string", dest="type",  default="all",  help="specify changetype ("", raybelief, twopass)")
parser.add_option("-n", "--nvals", action="store", type="string", dest="nvals", default="135",  help="specify n values (1, 13, 35, 135, etc)")
parser.add_option("-g", "--gpu",   action="store", type="string", dest="gpu",   default="gpu1", help="specify gpu (gpu0, gpu1, etc)")
parser.add_option("-o", "--gt",    action="store_true",           dest="gt",    default=False,  help="only render ground truth images")
parser.add_option("-i", "--imgType", action="store", type="string", dest="imgType", default="png", help="change image types (png, tif, tiff, etc)")
(options, args) = parser.parse_args()
print options
print args

#scene name, model name
scene_name = options.scene              #
scene_root = scene_registry.scene_root( scene_name ); #
MODEL      = options.xml.split("/")[0]

#set gpu
GPU = options.gpu

#n values to check for
ns = []
for n in options.nvals:
  ns.append( int(n) )

#change types
if options.type == "all":
  CHANGETYPES = [ "", "raybelief", "twopass" ] 
elif options.type in ["", "raybelief", "twopass"] :
  CHANGETYPES = [ options.type ] 
  print "Generating change images for change type: ", options.type
else: 
  print "unrecognized change type: ", options.type, "... exiting"
  sys.exit(-1)

# render only GT images, or all change imgs
ONLY_GTS   = options.gt        
#######################################################

#################################
#load up opencl scene
#################################
if not os.path.exists(scene_root + "/change/"):
  print "Model @ ", scene_root, " has no change directory"
  sys.exit(-1)
os.chdir(scene_root + "/change/")
scene_path = scene_root + "/" + options.xml 
scene = boxm2_scene_adaptor(scene_path, GPU);  

##################################
#load up images/cams to run CD on
##################################
if ONLY_GTS: 
  gts = glob(os.getcwd() + "/gt/*."+options.imgType); gts.sort(); 
  imgs = []; cams = []
  for gt in gts: 
    imgnum, ext = os.path.splitext( basename(gt) ); 
    bname = imgnum.split("_"); 
    img = os.getcwd() + "/imgs/" + bname[1] + "." + options.imgType; 
    cam = os.getcwd() + "/cams_krt/" + bname[1] + "_cam.txt"; 
    imgs.append( img ); 
    cams.append( cam ); 
  imgs.sort(); cams.sort(); gts.sort(); 
else :
  cimgDir = os.getcwd() + "/imgs/"
  if os.path.exists(cimgDir):
    imgs = glob(os.getcwd() + "/imgs/*." + options.imgType); imgs.sort(); 
    cams = glob(os.getcwd() + "/cams_krt/*.txt"); cams.sort(); 
  else:
    print "using model building images"
    imgs = glob(scene_root + "/nvm_out/imgs/*." + options.imgType)
    cams = glob(scene_root + "/nvm_out/cams_krt/*.txt")
  imgs.sort()
  cams.sort()
print imgs
assert len(imgs) == len(cams)

###########################################################
# render change img/cam pairs for each neighborhood value
# save images in <model_dir>/change/change_imgs/results_<model_type>_<change_type>/cd_NxN/
###########################################################
for CHANGETYPE in CHANGETYPES :
  outRoot = os.getcwd() + "/change_imgs/"
  for n in ns: 
    outdir = outRoot + "results_" + MODEL + "_" + CHANGETYPE + "/cd_%(#)dx%(#)d/"%{"#":n}; 
    render_changes(scene, imgs, cams, outdir, n, CHANGETYPE); 


####
#grab image number of ground truth image
#imgName = "/home/acm/Downloads/045391.png"
#imgName = os.getcwd() + "/imgs/045391.png"
#camName = os.getcwd() + "/cams_krt/045391_cam.txt"
#pcam        = load_perspective_camera(camName);  
#rimg,ni,nj  = load_image(imgName); 
## render exp
#expimg = scene.render(pcam, ni, nj);
##render change detection 
#cd_img = scene.change_detect(pcam, rimg, expimg, 5, "raybelief"); 
#save_image(cd_img, "test.tiff"); 

