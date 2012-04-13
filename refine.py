import random, os, sys, scene_registry;  
from boxm2_scene_adaptor import *; 
from optparse import OptionParser

#scene is given as first arg, figure out paths        #
parser = OptionParser()
parser.add_option("-s", "--scene", action="store", type="string", dest="scene", help="specify scene name")
parser.add_option("-x", "--xmlfile", action="store", type="string", dest="xml", default="uscene.xml", help="scene.xml file name (model/uscene.xml, model_fixed/scene.xml, rscene.xml)")
parser.add_option("-g", "--gpu",   action="store", type="string", dest="gpu",   default="gpu1", help="specify gpu (gpu0, gpu1, etc)")
parser.add_option("-t", "--thresh", action="store", type="float", dest="thresh", default=.3, help="Specify refine probability threshold")
(options, args) = parser.parse_args()
print options
print args

# handle inputs
#scene is given as first arg, figure out paths
scene_root = scene_registry.scene_root( options.scene ); 
os.chdir(scene_root)
scene_path = os.getcwd() + "/" + options.xml
if not os.path.exists(scene_path):
  print "SCENE NOT FOUND! ", scene_path
  sys.exit(-1)
scene = boxm2_scene_adaptor (scene_path, options.gpu);  
scene.refine(options.thresh);
scene.write_cache(); 
