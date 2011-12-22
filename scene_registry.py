import sys
import os, os.path

###############################################
# scene_registry.py
# holds my list of scenes to directory maps
###############################################

#SCENE PATHS
scene_paths = {}
scene_paths["apartments"] = "/home/acm/data/visualsfm/apts/"
scene_paths["hemenways"]  = "/home/acm/data/hemenways/"
scene_paths["capitol"]    = "/home/acm/data/capitol/"
scene_paths["downtown"]   = "/home/acm/data/downtown/"
scene_paths["downtown2"]  = "/home/acm/data/downtown2/"
scene_paths["biltmore"]   = "/home/acm/data/biltmore/"
scene_paths["eval06"]     = "/home/acm/data/Eval06/"
scene_paths["bandh"]      = "/home/acm/data/bandh/"
scene_paths["mall"]       = "/home/acm/data/mall/"
scene_paths["ppark"]      = "/home/acm/data/ppark/"
scene_paths["galactica"]  = "/home/acm/data/galactica/"

def scene_root(scene_name):
  if scene_name in scene_paths: 
    spath = scene_paths[scene_name]
  else: 
    spath = "/home/acm/data/" + scene_name + "/"
  if os.path.exists(spath):
    return spath
  else:
    print "SCENE: ", scene_name, " not found!!!!"
    print_scenes()
    sys.exit(-1)

def print_scenes():
  print "Confirmed Available scenes (may be more):"
  for scene, path in enumerate(scene_paths):
    print scene, " located at ", path
  
