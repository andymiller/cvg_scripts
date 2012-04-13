from boxm2_adaptor import *; 
import random, os, sys;  
from optparse import OptionParser

####################################################### 
# handle inputs                                       #
#scene is given as first arg, figure out paths        #
parser = OptionParser()
parser.add_option("-c", "--cams", action="store", type="string", dest="cams", help="location of bundler or nvm file")
parser.add_option("-i", "--imgs", action="store", type="string", dest="imgs", help="location of corresponding images")
parser.add_option("-a", "--app",  action="store", type="string", dest="app", default="boxm2_mog3_grey", help="appearance model - only valid boxm2_mog3_grey, and boxm2_gauss_rgb")
parser.add_option("-o", "--out",  action="store", type="string", dest="out", default="", help="if non empty, copy images to this directory")
parser.add_option("-b", "--bbox", action="store", type="string", dest="bbox", default="", help="Specify bbox: -b 1.2,3.4,2.4 ... If bbox and voxel size are specified, just create scene from that")
parser.add_option("-v", "--voxelSize", action="store", type="float", dest="voxelSize", default=-1.0, help="voxel size specified")
parser.add_option("-m", "--maxVoxels", action="store", type="int", dest="maxVoxels", default=-1, help="Specify maximum number of voxels in the scene")
parser.add_option("-n", "--numBlocks", action="store", type="int", dest="numBlocks", default=8, help="Specify number of blocks n (for n by n scene)")
(options, args) = parser.parse_args()
print options
print args

#pth = options.cams.split('/');
#flight = pth[-2].strip(); 
#site   = pth[-1].strip(); 
  
# bbox/voxelSize case
if options.voxelSize > 0.0 and options.bbox != "" :
  voxelSize = options.voxelSize
  print options.bbox
  bbox = [ float(x) for x in options.bbox.replace(')',' ').replace('(',' ').replace(',',' ').split() ]
  print bbox

  #params for save multi_block scene
  params = {}
  params['scene_dir'] = os.getcwd() 
  params['origin'] = bbox[0:3]

  #compute num vox on each side
  len_x = bbox[3] - bbox[0]
  len_y = bbox[4] - bbox[1]
  len_z = bbox[5] - bbox[2]
  print "Scene dimensions: ", len_x, len_y, len_z
  if len_x < 0 or len_y < 0 or len_z < 0:
    print "Invalid bounding box, lens: ", len_x, len_y, len_z
    sys.exit(-1)

  #set num voxel/voxel length
  params['num_vox'] = [int(len_x/voxelSize + .5), int(len_y/voxelSize + .5), int(len_z/voxelSize + .5)]
  params['vox_length'] = voxelSize
  params['num_blocks'] = [options.numBlocks, options.numBlocks, 1]

  #write scene out
  save_multi_block_scene(params)
  sys.exit(-1)

#otherwise use the bundle2scene option
print "Creating scene from bundle file: ", options.cams
uscene, rscene = bundle2scene(options.cams, options.imgs, options.app, options.out)
save_scene(uscene, "uscene"); 
save_scene(rscene, "rscene"); 


