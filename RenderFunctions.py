from boxm2_scene_adaptor import *; 
from bbas_adaptor import *;
from vil_adaptor import *;
from vpgl_adaptor import *;
import random, os, sys, math, scene_registry;  
import numpy as np;

###################################################
# Render helper functions -
# - pointsFromFile - parses point file (x,y,z)s
# - render_save - takes camera and saves image/camera in separate directories
#
#
###################################################



def pointsFromFile(fname):
  """ Point file format:
      <num points>
      <x>  <y>  <z>  
      <x>  <y>  <z>
  """
  f = open(fname, 'r')
  numPts = int(f.readline())
  print numPts
  pts = []
  for line in f:
    pt = [float(x) for x in line.strip().split()]
    pts.append(pt)
  return pts


def pathNormals(points):
  """ Computes the normal to each point (looking 
      45 degrees off nadir)
  """
  points = np.array(points)
  lookDirs = np.zeros(points.shape)
  lookPts = np.zeros(points.shape)

  #calculate direction of path (point1-point0)
  for idx in range(len(points)-1):
    pdir = points[idx+1] - points[idx]
    #assume zdir is0
    pdir[2] = 0.0
    updir = np.array([0.0, 0.0, 1.0])
    #norm dir to the "left"
    normDir = np.cross(pdir, updir)  
    #lookpoint on the ground
    lookPt = np.array([points[idx][0], points[idx][1], 0.0]) + points[idx][2]*normDir
    lookPts[idx] = lookPt

  #last look point just look at previous one
  lookPts[-1] = lookPts[-2]
  return lookPts


def render_save(scene, cam, globalIdx, trajDir, camDir, NI=1280, NJ=720):
  """method for rendering/saving/incrementing globalIdx"""
  #render image/convert to bimg
  expimg = scene.render(cam, NI, NJ);
  bimg   = convert_image(expimg); 
  exp_fname = trajDir + "/exp_%(#)03d.png"%{"#":globalIdx};
  save_image(bimg, exp_fname); 

  #save cam
  cam_name = camDir + "/cam_%(#)03d.txt"%{"#":globalIdx}
  save_perspective_camera(cam, cam_name)
  remove_from_db([cam, expimg, bimg])


def renderSpiral(lookPt, camCenter, dCamCenter, numImages):
  """ render a spiral around a look point returns cam center it ends up on
      lookPt (center of spiral)
      camCenter (az,inc,rad) w.r.t. lookPt
  """
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

def drift(look0, look1, camCenter, numImages):
  """ drift view to a new look point, smoothly """
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

def lookSmooth(point0, point1, camCenter, numImgs, dCamCenter=(0,0,0)): 
  """ take a camera looking at point0, with 
      center = (az, inc, rad), and look at poitn1
  """
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


