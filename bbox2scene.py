#!/usr/bin/python
from boxm2_adaptor import *; 
import random, os, sys, re

def parse_bbox_file(boxFile):
  """ Parses min and max point out of file of format: 
      bbox_min = (0,0,0)
      bbox_max = (300, 300, 8)    
  """
  lines = open(boxFile, 'r').readlines()
  pt1 = re.findall(r"[-+]?\d*\.\d+|\d+", lines[0])
  pt2 = re.findall(r"[-+]?\d*\.\d+|\d+", lines[1])

  #convert to floats
  pt1 = [float(x) for x in pt1]
  pt2 = [float(x) for x in pt2]
  return pt1, pt2


if __name__ == "__main__":

  #Check args
  if len(sys.argv) < 3:
    print "Usage: ./bbox2scene.py bbox.txt maxVoxels"
    sys.exit(-1)

  # box file
  boxFile = sys.argv[1]
  if not os.path.exists(boxFile):
    print "cannot find box file: ", boxFile
    sys.exit(-1)
  min_pt, max_pt = parse_bbox_file(boxFile)

  # grab digit from command line
  if not sys.argv[2].isdigit():
    print "second arg not digit: ", sys.argv[2]
    sys.exit(-1)
  maxVoxels = int(sys.argv[2])

  print "min point: ", min_pt
  print "max point: ", max_pt
  print "max voxels: ", maxVoxels

  #compute box dimensions
  len_x = max_pt[0] - min_pt[0]
  len_y = max_pt[1] - min_pt[1]
  len_z = max_pt[2] - min_pt[2]
  print "Scene dimensions: ", len_x, len_y, len_z
  if len_x < 0 or len_y < 0 or len_z < 0:
    print "Invalid bounding box, lens: ", len_x, len_y, len_z
    sys.exit(-1)

  #calculate total vol per voxel
  totalVol = len_x*len_y*len_z
  voxelVol = totalVol / float(maxVoxels)
  voxLen = voxelVol**(1.0/3.0)
  
  #params for save multi_block scene
  params = {}
  params['scene_dir'] = os.getcwd() 
  params['origin'] = min_pt

  #set num voxel/voxel length
  params['num_vox'] = [int(len_x/voxLen + .5), int(len_y/voxLen + .5), int(len_z/voxLen + .5)]
  params['vox_length'] = voxLen
  
  #TODO this is the tiling of the scene - this will subdivide the x and y plane into an 8x8
  params['num_blocks'] = [8, 8, 1]

  #write scene out
  save_multi_block_scene(params)
