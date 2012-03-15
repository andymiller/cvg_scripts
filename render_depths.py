import random, os, sys, scene_registry
from os.path import basename, splitext; 
from glob import glob; 
from optparse import OptionParser
from boxm2_scene_adaptor import *; 

############################################
# RENDER SPIRAL MAIN
############################################
if __name__ == "__main__":
  # handle inputs
  parser = OptionParser()
  parser.add_option("-s", "--scene", action="store", type="string", dest="scene", help="specify scene name")
  parser.add_option("-x", "--xmlfile", action="store", type="string", dest="xml", default="model/uscene.xml", help="scene.xml file name (model/uscene.xml, model_fixed/scene.xml, rscene.xml)")
  parser.add_option("-a", "--allImg", action="store_true", dest="allImg", default=False, help="render depth image for all available images") 
  (options, args) = parser.parse_args()
  print options
  print args
  
  #scene
  scene_root = scene_registry.scene_root( options.scene );
  scene_path = scene_root + "/" + options.xml; 
  if not os.path.exists(scene_path):
    print "Cannot find file: ", scene_path
    sys.exit(-1) 
  scene = boxm2_scene_adaptor(scene_path, "gpu"); 

  #render height map
  hdir = os.getcwd() + "/height/"
  if not os.path.exists(hdir):
    os.makedirs(hdir)
  z, var, x, y, prob, app = scene.render_height_map()
  save_image(z, hdir + "z.tiff")
  save_image(var, hdir + "var.tiff")
  save_image(x, hdir + "x.tiff")
  save_image(y, hdir + "y.tiff")
  save_image(prob, hdir + "prob.tiff")
  save_image(app, hdir + "appearance.tiff")

  #if specified to render all images
  if options.allImg:
    #render all images, not just GT imgs
    imgs = glob(os.getcwd() + "/imgs/*.png"); imgs.sort(); 
    cams = glob(os.getcwd() + "/cams_krt/*.txt"); cams.sort(); 

    #write depth images out
    outdir = os.getcwd() + "/depths/" + scene_type + "/"; 
    if not os.path.exists(outdir):
      os.makedirs(outdir); 

    for idx, img in enumerate(imgs):
      #grab image number of ground truth image
      imgnum, ext  = os.path.splitext( basename(img) ); 
      cam          = load_perspective_camera(cams[idx]); 
      dimg, varimg = scene.render_depth(cam);
      save_image(dimg,   outdir + imgnum + ".tiff"); 
      save_image(varimg, outdir + imgnum + "_var.tiff"); 
