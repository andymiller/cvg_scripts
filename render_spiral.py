from boxm2_scene_adaptor import *; 
from bbas_adaptor import *;
from vil_adaptor import *;
from vpgl_adaptor import *;
import numpy, random, os, sys, math, scene_registry;  
from optparse import OptionParser

####################################################### 
# handle inputs                                       #
#scene is given as first arg, figure out paths        #
parser = OptionParser()
parser.add_option("-s", "--scene", action="store", type="string", dest="scene", help="specify scene name")
parser.add_option("-x", "--xmlfile", action="store", type="string", dest="xml", default="model/uscene.xml", help="scene.xml file name (model/uscene.xml, model_fixed/scene.xml, rscene.xml)")
parser.add_option("-g", "--gpu",   action="store", type="string", dest="gpu",   default="gpu1", help="specify gpu (gpu0, gpu1, etc)")
parser.add_option("-m", "--maxFrames", action="store", type="int", dest="maxFrames", default=500, help="max number of frames to render")
parser.add_option("-r", "--radius", action="store", type="float", dest="radius", default=10.0, help="starting cam radius")
parser.add_option("-i", "--incline", action="store", type="string", dest="incline", default="38:45", help="incline change throughout spiral in degrees (ex 38:45)")
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
#######################################################

#################################################
# Set some update parameters
model_name = "model"
GPU = "gpu0"
NUM_IMAGES = options.maxFrames
NI=1280
NJ=720

#ensure trajectory images can be written out
trajDir = os.getcwd() + "/spiral/"
if not os.path.exists(trajDir):
  os.mkdir(trajDir);
camDir = os.getcwd() + "/spiral_cams/"
if not os.path.exists(camDir):
  os.mkdir(camDir)
################################################

#should initialize a GPU
os.chdir(scene_root);
scene_path = scene_root + "/" + options.xml
scene = boxm2_scene_adaptor(scene_path, GPU);  
(sceneMin, sceneMax) = scene.bounding_box(); 

#init trajectory, look at center point - this can drift
startInc, endInc = [int(x) for x in options.incline.split(":")]
radius   = max(options.radius, 1.4*(sceneMax[0]-sceneMin[0])); 
modCenter = numpy.add(sceneMax, sceneMin)/2.0

########################################
#Generate camera params - fLenght, ppoint
########################################
fLength = math.sqrt(NI*NI+NJ*NJ)
ppoint = (NI/2, NJ/2)

###################################################
# method for rendering/saving/incrementing globalIdx
def render_save(cam):
  global globalIdx
  expimg = scene.render(cam, NI, NJ);
  bimg   = convert_image(expimg); 
  exp_fname = trajDir + "/exp_%(#)03d.png"%{"#":globalIdx};
  save_image(bimg, exp_fname); 
  #save cam
  cam_name = camDir + "/cam_%(#)03d.txt"%{"#":globalIdx}
  save_perspective_camera(cam, cam_name)
  #remove_from_db([cam, expimg, bimg])
  globalIdx+=1

###################################################################
#render a spiral around a look point returns cam center it ends up on
#lookPt (center of spiral)
#camCenter (az,inc,rad) w.r.t. lookPt
def renderSpiral(lookPt, camCenter, dCamCenter, numImages):
  global globalIdx
  for idx in range(numImages):
    print "Rendering # ", idx, "of", numImages
    #create cam, and render
    currAz,currInc,currR = camCenter
    center = get_camera_center(currAz, currInc, currR, lookPt)
    cam = create_perspective_camera( (fLength,fLength), ppoint, center, lookPt )
    render_save(cam)
    #increment az, incline and radius
    camCenter = numpy.add(camCenter, dCamCenter)
  return camCenter

#drift view to a new look point, smoothly
def drift(look0, look1, camCenter, numImages):
  #calc input XYZ center about look0
  currAz, currInc, currR = camCenter
  center = get_camera_center(currAz, currInc, currR, look0)
  #calc drift val, and store lookPt
  lookPt = look0
  drift = numpy.subtract(look1,look0)/numImages
  for idx in range(numImages):
    cam = create_perspective_camera( (fLength,fLength), ppoint, center, lookPt )
    render_save(cam)
    lookPt = numpy.add(lookPt, drift)
    center = numpy.add(center, drift)
  return center

###############################################
#take a camera looking at point0, with center = (az, inc, rad), 
#and look at poitn1
def lookSmooth(point0, point1, camCenter, numImgs, dCamCenter=(0,0,0)): 
  global globalIdx
  print "gazing from ", point0, "to", point1
  az, inc, rad = camCenter; 
  lDiff = numpy.subtract(point1, point0)
  dLook = numpy.divide(lDiff, numImgs)
  lpoint = point0
  for idx in range(numImgs):
    #create cam, and render
    center = get_camera_center(az, inc, rad, modCenter)
    cam = create_perspective_camera( (fLength,fLength), ppoint, center, lpoint )
    expimg = scene.render(cam, NI, NJ);
    bimg   = convert_image(expimg); 
    exp_fname = trajDir + "/exp_%(#)03d.png"%{"#":globalIdx};
    globalIdx+=1
    save_image(bimg, exp_fname); 
    remove_from_db([cam, expimg, bimg])

    #increment az, incline and radius
    lpoint = numpy.add(lpoint, dLook)


###########################################
####Render the various maneuvers###########
###########################################
# Initialize list of look points to spiral around
pts = [ modCenter ]
pts.append( (.2308, -.295, .0279) )
pts.append( (-.106, 0.297, .021) )
globalIdx = 0

#generate starting point, and delta cam center
currR = radius
currInc = startInc
currAz = -90.0
dr = - (radius/1.45) / NUM_IMAGES
dAz = 360.0 / NUM_IMAGES
dInc = (endInc-startInc)/NUM_IMAGES

#render first spiral
dcam = (dAz, dInc, dr)
center = renderSpiral(pts[0], (currAz, currInc, currR), dcam, NUM_IMAGES)
#drift to next center
cartCenter = drift(pts[0], pts[1], center, NUM_IMAGES/4)
sphereCenter = cart2sphere( cartCenter, pts[1] )
#sphereCenter = (sphereCenter[0],-sphereCenter[1],sphereCenter[2])

#render next spiral
numImg = NUM_IMAGES/2
dcam = (360/numImg, 0, 0)
center = renderSpiral(pts[1], sphereCenter,dcam,numImg) 
#drift to next center
cartCenter = drift(pts[1], pts[2], center, NUM_IMAGES/4)
sphereCenter = cart2sphere( cartCenter, pts[2] )
#sphereCenter = (sphereCenter[0],-sphereCenter[1],sphereCenter[2])

#render next spiral
numImg = NUM_IMAGES/2
dcam = (360/numImg, 0, 0)
center = renderSpiral(pts[2], sphereCenter, dcam, numImg)

#mencoder "mf://*.png" -mf fps=18 -o demo.avi -ovc lavc -lavcopts vcodec=msmpeg4v2:vbitrate=24000000

