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

#generate point cloud
boxm2_batch.init_process("boxm2ExtractPointCloudProcess");
boxm2_batch.set_input_from_db(0,scene.scene);
boxm2_batch.set_input_from_db(1,scene.cpu_cache);
boxm2_batch.set_input_float(2,options.prob); #prob threshold
boxm2_batch.run_process();

boxm2_batch.init_process("boxm2ExportOrientedPointCloudProcess");
boxm2_batch.set_input_from_db(0,scene.scene);
boxm2_batch.set_input_from_db(1,scene.cpu_cache);
boxm2_batch.set_input_string(2,options.output);
boxm2_batch.run_process();

