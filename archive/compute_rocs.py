from boxm2_change_roc import *
from vil_adaptor import *
from glob import glob; 
from numpy import *
import pylab
import os
from os.path import basename, splitext; 

#load up ground truth imgs
gts = glob(os.getcwd() + "/gt/*.png"); gts.sort(); 
gts = gts[2:3]; 

#load up change results  
cdimgs = { "1x1":   glob(os.getcwd() + "/results/cd_1x1/*.tiff"),
           "3x3":   glob(os.getcwd() + "/results/cd_3x3/*.tiff"),
           "5x5":   glob(os.getcwd() + "/results/cd_5x5/*.tiff"),
           "7x7":   glob(os.getcwd() + "/results/cd_7x7/*.tiff"),
           "1x1 rb": glob(os.getcwd() + "/results/cd_1x1_rb/*.tiff"),
           "3x3 rb": glob(os.getcwd() + "/results/cd_3x3_rb/*.tiff"),
           "5x5 rb": glob(os.getcwd() + "/results/cd_5x5_rb/*.tiff"),
           "7x7 rb": glob(os.getcwd() + "/results/cd_7x7_rb/*.tiff"),
          }
tprs = []; fprs = []; aucs = []; 
for key, cdir in cdimgs.items(): 
  tprs.append([]); 
  fprs.append([]); 
  aucs.append([]); 
  cdir.sort(); 
          
#calc AUC for each image in GT
for gt in gts : 

  #grab image number of ground truth image
  gt_img,ni,nj = load_image(gt); 
  
  #go through each 1x1, 3x3, 5x5
  for idx, cdimg in enumerate(cdimgs.items()): 
    
    #grab 2nd CD image
    cdir = cdimg[1]; 
    cd = cdir[2:3][0]; 
    print "Loading image: ", cd; 
    cd_img,ni,nj = load_image(cd); 

    #calc ROC and AUC
    tpr, fpr = calc_roc(cd_img, gt_img, False); 
    auc = area_under_curve(tpr, fpr); 
    tprs[idx].append(tpr); 
    fprs[idx].append(fpr); 
    aucs[idx].append(auc); 


for idx, cdimg in enumerate(cdimgs.items()):
  line = pylab.plot( fprs[idx][0], tprs[idx][0] ); 
  #lbl  = "%(#)01d by %(#)01d"%{"#":ns[idx]}; 
  pylab.setp(line, label=cdimg[0]);
  
#show with legend
l = pylab.legend(); 
pylab.title("Change Detection ROC Comparison: Apartment Image " + basename(gts[0])); 
pylab.show();



	

