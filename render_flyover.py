from boxm2_scene_adaptor import *; 
from bbas_adaptor import *;
from vil_adaptor import *;
from vpgl_adaptor import *;
from RenderFunctions import *;
import numpy, random, os, sys, math, scene_registry;  
from optparse import OptionParser
import matplotlib.pyplot as plt


############################################
# RENDER SPIRAL MAIN
############################################
if __name__ == "__main__":
  # handle inputs
  parser = OptionParser()
  parser.add_option("-s", "--scene", action="store", type="string", dest="scene", help="specify scene name")
  parser.add_option("-x", "--xmlfile", action="store", type="string", dest="xml", default="model/uscene.xml", help="scene.xml file name (model/uscene.xml, model_fixed/scene.xml, rscene.xml)")
  parser.add_option("-g", "--gpu",   action="store", type="string", dest="gpu",   default="gpu1", help="specify gpu (gpu0, gpu1, etc)")
  parser.add_option("-m", "--maxFrames", action="store", type="int", dest="maxFrames", default=500, help="max number of frames to render")
  parser.add_option("-i", "--incline", action="store", type="float", dest="incline", default=38.0, help="incline of look direction off tangent of path (determines look point)")
  parser.add_option("-p", "--points", action="store", type="string", dest="pointsFile", default="", help="Include points file as center points of spirals (no file defaults to center of model)")
  parser.add_option("-v", "--visualize", action="store_true", dest="visualize", default=False, help="just visualize the path in matplotlib")
  parser.add_option("-n", "--numBetween", action="store", type="int", dest="numBetween", default=0, help="specify number of points to interpolate between points in trajectory file (for smoothness)")
  (options, args) = parser.parse_args()
  if not os.path.exists(options.pointsFile):
    print "bad pointsfile: ", options.pointsFile
    sys.exit(-1)

  # grab scene
  scene_root = scene_registry.scene_root( options.scene ); #
  scene_path = scene_root + "/" + options.xml; 
  if not os.path.exists(scene_path):
    print "Cannot find file: ", scene_path
    sys.exit(-1) 

  #output frame size
  NI,NJ=1280,720

  # ensure trajectory images can be written out
  trajDir = os.getcwd() + "/spiral/"
  if not os.path.exists(trajDir):
    os.mkdir(trajDir);
  camDir = os.getcwd() + "/spiral_cams/"
  if not os.path.exists(camDir):
    os.mkdir(camDir)

  #should initialize a GPU
  os.chdir(scene_root);
  scene = boxm2_scene_adaptor(scene_path, options.gpu);  

  #Generate camera params - fLenght, ppoint
  fLength = math.sqrt(NI*NI+NJ*NJ)
  ppoint = (NI/2, NJ/2)
  incline = options.incline

  ###########################################
  ####Render the various maneuvers###########
  ###########################################
  # Initialize list of look points to spiral around
  pts = pointsFromFile(options.pointsFile)
  pts = np.array(pts)
  print "Trajectory consists of %d points"%len(pts)

  #compute dense points
  pts = interpolatePoints(pts, options.numBetween)
  print "Dense trajectory consists of %d points"%len(pts)

  #compute look directions for each point
  lookPts = pathNormals(pts, incline)
  lookDirs = normalize(lookPts - pts)
  lookPts = pts + lookDirs

  #visualize trajectory and look dirs
  if options.visualize:
    #compute unit normal
    plt.plot(pts[:,0], pts[:,1])
    for idx,p in enumerate(pts):
      line = np.array([p[0:2], p[0:2] + lookDirs[idx][0:2]])
      plt.plot(line[:,0], line[:,1], 'r')

    #make start point easy to see
    plt.plot(pts[20,0], pts[20,1], 'gs')
    plt.plot(lookPts[20,0], lookPts[20,1], 'gd')
    
    plt.show()
    sys.exit(-1)

  #render from each points viewpoint
  globalIdx = 0
  for idx,pt in enumerate(pts):
    cam = create_perspective_camera( (fLength, fLength), ppoint, pt, lookPts[idx] )
    render_save(scene, cam, globalIdx, trajDir, camDir)
    globalIdx += 1

  #mencoder "mf://*.png" -mf fps=18 -o demo.avi -ovc lavc -lavcopts vcodec=msmpeg4v2:vbitrate=24000000
 
