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
parser.add_option("-p", "--prob", action="store", type="float", dest="prob", default=.75, help="Specify probability threshold for points in point cloud")
parser.add_option("-o", "--output", action="store", type="string", dest="output", default="out.ply", help="specify point file (.ply, .pcd...)")
parser.add_option("-b", "--blocks", action="store", type="string", dest="blocks", default="all", help="specify a certain block (jkl, eg 1,3,5=> i=1,j=3,k=5)")
parser.add_option("-a", "--allInfo", action="store_true", dest="allInfo", default=False, help="Turn on all point info (prob, vis, etc)")
parser.add_option("-n", "--normals", action="store_true", dest="normals", default=False, help="Store normals for each point in the cloud")
(options, args) = parser.parse_args()
print options
print args
######################################################


#initialize scene
scene_root = scene_registry.scene_root( options.scene ); 
scene_path = scene_root + "/" + options.xml
if not os.path.exists(scene_path):
  print "Cannot find file: ", scene_path
  sys.exit(-1) 
os.chdir(scene_root);
scene = boxm2_scene_adaptor(scene_path)
#(sceneMin, sceneMax) = scene.bounding_box()

#determine which block to use
#computer deriv property (for getting normals
boxm2_batch.init_process("boxm2CppComputeDerivativeProcess");
boxm2_batch.set_input_from_db(0,scene.scene);
boxm2_batch.set_input_from_db(1,scene.cpu_cache);
boxm2_batch.set_input_float(2,options.prob); #prob threshold
boxm2_batch.set_input_float(3,-1); #normal t
boxm2_batch.set_input_string(4, "/home/acm/vxl/src/contrib/brl/bseg/bvpl/doc/taylor2_5_5_5/Ix.txt");
boxm2_batch.set_input_string(5, "/home/acm/vxl/src/contrib/brl/bseg/bvpl/doc/taylor2_5_5_5/Iy.txt");
boxm2_batch.set_input_string(6, "/home/acm/vxl/src/contrib/brl/bseg/bvpl/doc/taylor2_5_5_5/Iz.txt");
if options.blocks != "all":
  blocks = options.blocks.split(",")
  boxm2_batch.set_input_int(7, int(blocks[0]))
  boxm2_batch.set_input_int(8, int(blocks[1]))
  boxm2_batch.set_input_int(9, int(blocks[2]))
boxm2_batch.run_process();

#export point cloud...
if options.normals:
  pointType = "PointNormal"
else:
  pointType = "Point"
boxm2_batch.init_process("boxm2ExportPointCloudXYZProcess");
boxm2_batch.set_input_from_db(0,scene.scene);
boxm2_batch.set_input_from_db(1,scene.cpu_cache);
boxm2_batch.set_input_string(2, options.output);
boxm2_batch.set_input_bool(3,1);  #output prob vis etc?
boxm2_batch.set_input_float(4,-1);  #vis threshold?
boxm2_batch.set_input_float(5,-1); #normal magnitude threshold
boxm2_batch.set_input_string(6, pointType);
boxm2_batch.run_process();

