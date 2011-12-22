from boxm2_adaptor import *; 
import random, os, sys;  
from optparse import OptionParser

##
#basedir = os.getcwd(); 
#nvm = '/home/acm/data/visualsfm/flight2/jpgs/45151_47821_fixf_out.nvm'
#png = '/home/acm/data/visualsfm/flight2/site_2'
#
##downtown nvm
#nvm = "/home/acm/data/visualsfm/flight4/site_5/jpgs/51401_58991_fixf_out.nvm"
#png = "/home/acm/data/visualsfm/flight4/site_5"
#
##bandh
#nvm = "/home/acm/data/bandh/nvm_out/2300_6530_fixedf_out.nvm"
#png = "/home/acm/data/bandh/nvm_out/imgs/"
#
##ppark  
#nvm = "/home/acm/data/ppark/nvm_out/14020_17410_fixf_out.nvm"
#png = "/home/acm/data/ppark/nvm_out/imgs/"  
#
##mall  
#nvm = "/home/acm/data/mall/nvm_out/33151_35161_fixf_out.nvm"
#png = "/home/acm/data/mall/nvm_out/imgs/"  
 
####################################################### 
# handle inputs                                       #
#scene is given as first arg, figure out paths        #
parser = OptionParser()
parser.add_option("-c", "--cams", action="store", type="string", dest="cams", help="location of bundler or nvm file")
parser.add_option("-i", "--imgs", action="store", type="string", dest="imgs", help="location of corresponding images")
parser.add_option("-a", "--app",  action="store", type="string", dest="app", default="boxm2_mog3_grey", help="appearance model - only valid boxm2_mog3_grey, and boxm2_gauss_rgb")
parser.add_option("-o", "--out",  action="store", type="string", dest="out", default="", help="if non empty, copy images to this directory")
(options, args) = parser.parse_args()
print options
print args
 
#pth = options.cams.split('/');
#flight = pth[-2].strip(); 
#site   = pth[-1].strip(); 
  
print "Creating scene from bundle file: ", options.cams
uscene, rscene = bundle2scene(options.cams, options.imgs, options.app, options.out)
save_scene(uscene, "uscene"); 
save_scene(rscene, "rscene"); 


