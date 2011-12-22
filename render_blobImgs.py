from boxm2_scene_adaptor import *; 
from brip_adaptor import *;
from bbas_adaptor import *;
from change.helpers import *;
from os.path import basename, splitext; 
from glob import glob; 
import random, os, sys, numpy, pylab, scene_registry;  
from optparse import OptionParser

####################################################### 
# handle inputs                                       #
#scene is given as first arg, figure out paths        #
parser = OptionParser()
parser.add_option("-s", "--scene", action="store", type="string", dest="scene", help="specify scene name")
parser.add_option("-m", "--model", action="store", type="string", dest="model", default="model",help="model name (model, model_fixed, model_full)")
parser.add_option("-k", "--kl",    action="store_true",           dest="kl",    default=False,  help="do blob-wise kl div elimination")
parser.add_option("-l", "--lower", action="store", type="float",  dest="lower", default=.1,     help="lower blob threshold")
parser.add_option("-u", "--upper", action="store", type="float",  dest="upper", default=.9,     help="upper blob threshold")
parser.add_option("-t", "--type",  action="store", type="string", dest="type",  default="all",  help="specify changetype ("", raybelief, twopass)")
parser.add_option("-g", "--gpu",   action="store", type="string", dest="gpu",   default="gpu1", help="specify gpu (gpu0, gpu1, etc)")
parser.add_option("-o", "--gt",    action="store_true",           dest="gt",    default=False,  help="only render ground truth images")
parser.add_option("-n", "--nvals", action="store", type="string", dest="nvals", default="135",  help="specify n values (1, 13, 35, 135, etc)")
(options, args) = parser.parse_args()
print options
print args
print options.scene

scene_name = options.scene               #
scene_root = scene_registry.scene_root( scene_name ); #
MODEL      = options.model  # directory name for model
DO_KL_ELIMINATION = options.kl;
LOWER = options.lower
UPPER = options.upper
ONLY_GTS = options.gt         # render only GT images, or all change imgs

#set gpu
if options.gpu in ["gpu0", "gpu1"]:
  GPU = options.gpu
else: 
  GPU = "gpu1"

#change image dirs and n values to check for
NS = []
for n in options.nvals:
  NS.append( int(n) )
if options.type == "all":
  CHANGE_IMG_DIRS = [ "change_imgs/results_" + MODEL + "_" + "", 
                      "change_imgs/results_" + MODEL + "_" + "raybelief",
                      "change_imgs/results_" + MODEL + "_" + "twopass" ]
elif options.type in ["", "raybelief", "twopass"] :
  CHANGE_IMG_DIRS = [ "change_imgs/results_" + MODEL + "_" + options.type]
  print "Generating blob images for change type: ", options.type
USE_DEPTH_THRESH = False;
########################################################

#################################
#load up opencl scene
#################################
if not os.path.exists(scene_root + "/change/"):
  print "Model @ ", scene_root, " has no change directory"
  sys.exit(-1)
os.chdir(scene_root + "/change/")
scene_path = "../" + MODEL + "/uscene.xml";  
if not os.path.exists(scene_path):
  print "Scene @ ", scene_path, " does not exist!!!!!"
  sys.exit(-1)
scene = boxm2_scene_adaptor(scene_path,GPU);  

#################################
#in images (new frames) and depth imgs
#################################
inimgs = glob(os.getcwd() + "/imgs/*.png"); inimgs.sort(); 
incams = glob(os.getcwd() + "/cams_krt/*.txt"); incams.sort();
assert len(inimgs) == len(incams)

#depth images for r scene and u scene
if USE_DEPTH_THRESH :
  dimgs1 = glob(os.getcwd() + "/depths/rscene/*.tiff"); dimgs1.sort();
  dimgs2 = glob(os.getcwd() + "/depths/uscene/*.tiff"); dimgs2.sort();
  assert len(dimgs1) == len(dimgs2)  
  assert len(dimgs2) == len(inimgs) 
      
##############################################################
#save blob images/vis images
##############################################################
blobDir = os.getcwd() + "/blob_images/"; 
if not os.path.exists(blobDir) :
  os.makedirs(blobDir);   
  
#for each cd result directory, render threshed images
result_dirs = []; 
for imgDir in CHANGE_IMG_DIRS :
  for n in NS:
    resDir = os.getcwd() + "/" + imgDir + "/cd_%dx%d"%(n,n)
    if os.path.exists(resDir):
      result_dirs.append(resDir) # += glob( os.getcwd() + "/" + imgDir + "/*" ); 
result_dirs.sort(); 
print result_dirs
for d in result_dirs: 

  #make appropriate dir 
  splitpath = d.split('/'); 
  imDir = blobDir + splitpath[-2] + "_" + splitpath[-1] + "/"; 
  if not os.path.exists(imDir) :
    os.makedirs(imDir);   

  #render thresholded images
  for thresh in numpy.arange(LOWER, UPPER, .05): 
    if DO_KL_ELIMINATION:
      outdir = imDir + "/blobs_kl_" + str(thresh) + "/"; 
    else:
      outdir = imDir + "/blobs_" + str(thresh) + "/"; 
    if not os.path.exists(outdir) :
      os.makedirs(outdir); 

    #load up change images
    imgs  = glob(d + "/*.tiff"); imgs.sort()
    for idx, img in enumerate(imgs):
      
      #load input image (new frame)
      inImg, ni, nj = load_image(inimgs[idx]); 
      
      #load change image
      if USE_DEPTH_THRESH :
        d1,ni,nj   = load_image(dimgs1[idx]); 
        d2,ni,nj   = load_image(dimgs2[idx]); 
        cimg,ni,nj = load_image(img); 
        bimg       = blob_change_detection( cimg, thresh, d1, d2)
      else : 
        cimg,ni,nj = load_image(img); 
        bimg       = blob_change_detection( cimg, thresh)

      #do KL div based blob pruning
      if DO_KL_ELIMINATION :
        #gradient on input image
        greyImg = convert_image(inImg, "grey"); 
        inDx, inDy, inMag = gradient(greyImg); 
        #expected image gradient
        inCam  = load_perspective_camera(incams[idx]); 
        expImg = scene.render(inCam); 
        expDx, expDy, expMag = gradient(expImg); 
        #kl img and new blob img
        kl_img, new_blobs = blobwise_kl_div(inMag, expMag, bimg); 
        oldB = bimg;
        bimg = new_blobs

      ###########################
      #render visualize image
      vis_img  = visualize_change(bimg, inImg, thresh); 

      ################################
      # save vis image in new blob img dir
      imgnum, ext = os.path.splitext( basename(img) ); 
      img_name  = outdir + "/" + imgnum + ".png"; 
      save_image(vis_img, img_name); 
      
      #######################
      #clean up images 
      remove_from_db( [inImg, cimg, vis_img] );
      if DO_KL_ELIMINATION :
        remove_from_db( [greyImg, inDx, inDy, inMag, expImg, expDx, expDy, expMag, kl_img, new_blobs, oldB]);
  
