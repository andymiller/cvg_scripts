from boxm2_scene_adaptor import *; 
from bbas_adaptor import *;
from vil_adaptor import *;
from vpgl_adaptor import *;
import numpy, random, os, sys, math, scene_registry;  
from optparse import OptionParser

if __name__ == "__main__":
  # handle inputs
  parser = OptionParser()
  parser.add_option("-s", "--scene", action="store", type="string", dest="scene", help="specify scene name")
  parser.add_option("-x", "--xmlfile", action="store", type="string", dest="xml", default="model/uscene.xml", help="scene.xml file name (model/uscene.xml, model_fixed/scene.xml, rscene.xml)")
  (options, args) = parser.parse_args()
  print options
  print args

  scene_root = scene_registry.scene_root( options.scene ); #
  scene_path = scene_root + "/" + options.xml; 
  if not os.path.exists(scene_path):
    print "Cannot find file: ", scene_path
    sys.exit(-1) 

  #should initialize a GPU
  scene = boxm2_scene_adaptor(scene_path);  
  (sceneMin, sceneMax) = scene.bounding_box(); 
  print "Scene bounding box: ", sceneMin, " to ", sceneMax
 
