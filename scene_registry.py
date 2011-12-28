import sys
import os, os.path

###############################################
# scene_registry.py
# holds my list of scenes to directory maps
###############################################

#SCENE PATHS
scene_paths = {}
#scene_paths["apartments"] = "/home/acm/data/visualsfm/apts/"
#scene_paths["hemenways"]  = "/home/acm/data/hemenways/"
#scene_paths["capitol"]    = "/home/acm/data/capitol/"
#scene_paths["downtown"]   = "/home/acm/data/downtown/"
#scene_paths["downtown2"]  = "/home/acm/data/downtown2/"
#scene_paths["biltmore"]   = "/home/acm/data/biltmore/"
#scene_paths["eval06"]     = "/home/acm/data/Eval06/"
#scene_paths["bandh"]      = "/home/acm/data/bandh/"
#scene_paths["mall"]       = "/home/acm/data/mall/"
#scene_paths["ppark"]      = "/home/acm/data/ppark/"
#scene_paths["galactica"]  = "/home/acm/data/galactica/"

data_candidates = [ 
                    "/data/",
                    "/data/models",
                    os.path.expanduser("~/data/"),
                    os.path.expanduser("~/data/models/")
                  ]


def scene_root(scene_name):
  if not scene_name or scene_name == "": 
    print "NO SCENE GIVEN!"
    sys.exit(-1)
  for cand in data_candidates:
    if os.path.exists( cand+"/"+scene_name ):
      return cand+"/"+scene_name
  
  #otherwise no path, throw error
  print "SCENE: ", scene_name, " not found!!!!"
  print_scenes()
  sys.exit(-1)

def print_scenes():
  for cand in data_candidates:
    print "Checking for data in: ", cand
    if os.path.exists(cand):
      print os.listdir(cand)
    else:
      print "  ... ", cand, " not found!"
  
