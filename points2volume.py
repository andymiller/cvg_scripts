from boxm2_scene_adaptor import *; 
from boxm2_adaptor import save_multi_block_scene
from vpgl_adaptor import *
from vil_adaptor import *
import scene_registry
import os, sys 
from optparse import OptionParser

####################################################### 
# handle inputs                                       #
#scene is given as first arg, figure out paths        #
parser = OptionParser()
parser.add_option("-s", "--scene", action="store", type="string", dest="scene", help="specify scene name")
parser.add_option("-x", "--xmlfile", action="store", type="string", dest="xml", default="model/uscene.xml", help="scene.xml file name (model/uscene.xml, model_fixed/scene.xml, rscene.xml)")
parser.add_option("-p", "--points", action="store", type="string", dest="points", default="", help="specify point file (.ply, .pcd...)")
(options, args) = parser.parse_args()
print options
print args
######################################################

#check for point file
if not os.path.exists(options.points):
  print "Can't find points file:", options.points
  sys.exist(-1)

#initialize scene
scene_root = scene_registry.scene_root( options.scene ); 
scene_path = scene_root + "/" + options.xml
if not os.path.exists(scene_path):
  print "Cannot find file: ", scene_path
  sys.exit(-1) 
os.chdir(scene_root);
scene = boxm2_scene_adaptor(scene_path)
#(sceneMin, sceneMax) = scene.bounding_box()

#export point cloud...
boxm2_batch.init_process("boxm2CppPointsToVolumeProcess");
boxm2_batch.set_input_from_db(0,scene.scene);
boxm2_batch.set_input_from_db(1,scene.cpu_cache);
boxm2_batch.set_input_string(2, options.points);
boxm2_batch.run_process();



#render for testing
#NI=1280
#NJ=720
#fLength = math.sqrt(NI*NI+NJ*NJ)
#ppoint = (NI/2, NJ/2)
#look = (71,-30,0)
#currInc = 75
#currAz = 300
#currR = 200
#center = get_camera_center(currAz, currInc, currR, look)
#cam = create_perspective_camera( (fLength, fLength), ppoint, center, look)
#exp = scene.render(cam)
#expB = convert_image(exp)
#save_image(expB, "/home/acm/Dropbox/test.png")
##


scene.write_cache()
