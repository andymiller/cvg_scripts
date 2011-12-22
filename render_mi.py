from boxm2_scene_adaptor import *; 
from change.helpers import *;
from brip_adaptor import *; 
from vil_adaptor import *; 
import random, os, sys;  
import numpy
import pylab
from glob import glob; 


#####################################################
# SCRIPT PARAMETERS
CHANGE_IMG_DIRS = [   
                    #"change_imgs/results_thresh.25/", 
                    #"change_imgs/results_rb/",
                    #"change_imgs/results_thresh.75/",
                    #"change_imgs/results_max_batch/",
                    #"change_imgs/results_max_online/",
                    "change_imgs/results_fixed/",
                    "change_imgs/results_fixed_multires/",
                  ]  
#######################################################

#IMAGE_NUM = "046831"
IMAGE_NUM = "045361"

#load up opencl scene
scene_path = "../model_fixed/uscene.xml";  
scene = boxm2_scene_adaptor(scene_path, False, "gpu");  

#in image and gradients
inPath = "/home/acm/data/visualsfm/apts/change/imgs/" + IMAGE_NUM + ".png"
inImg, ni, nj = load_image(inPath); 
greyImg = convert_image(inImg, "grey"); 
inDx, inDy, inMag = gradient(greyImg); 

#expected image
inCamPath = "/home/acm/data/visualsfm/apts/change/cams_krt/" + IMAGE_NUM + "_cam.txt"
inCam  = load_perspective_camera(inCamPath); 
expImg = scene.render(inCam); 
expDx, expDy, expMag = gradient(expImg); 

#change image -> blob image
changePath = "/home/acm/data/visualsfm/apts/change/change_imgs/results_fixed_multires/cd_5x5/cd_" + IMAGE_NUM + ".tiff"
changeImg, ni, nj = load_image(changePath); 
thresh = .25
bimg   = blob_change_detection( changeImg, thresh )


###############
kl_img, new_blobs = blobwise_kl_div(inMag, expMag, bimg); 
#visualize blob image
vis_img  = visualize_change(new_blobs, inImg, thresh); 
save_image(vis_img, "test_new.png"); 
vis_img  = visualize_change(bimg, inImg, thresh); 
save_image(vis_img, "test_old.png"); 






