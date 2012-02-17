import os, sys
from optparse import OptionParser

def nvm2ply(nvm, ply):
  assert( os.path.exists(nvm) )
  f = open(nvm, "r")
  out = open(ply, "w")

  #read first line (header)
  header = f.readline();

  #read num cams
  numCams = int(f.readline())

  #skip over cams
  for i in range(numCams):
    skipped = f.readline();

  #read in num points
  numPoints = int(f.readline())

  #write ply header
  out.write("ply\nformat ascii 1.0\n")
  out.write("element vertex %i\n"%numPoints)
  out.write("property float x\n")
  out.write("property float y\n")
  out.write("property float z\n")
  out.write("property uchar red\n")
  out.write("property uchar green\n")
  out.write("property uchar blue\n")
  out.write("end_header\n")

  #write points
  for i in range(numPoints):
    line = f.readline().split();
    p = line[0:3]
    c = line[3:6]
    out.write("%s %s %s %s %s %s\n"%(p[0],p[1],p[2],c[0],c[1],c[2]))

if __name__ == "__main__":
 
  #scene is given as first arg, figure out paths        #
  parser = OptionParser()
  parser.add_option("-n", "--nvm", action="store", type="string", dest="nvm", help="specify nvm file")
  parser.add_option("-o", "--out", action="store", type="string", dest="out", default="out.ply", help="specify ply file output") 
  (options, args) = parser.parse_args()

  #convert nvm
  nvm2ply(options.nvm, options.out);

