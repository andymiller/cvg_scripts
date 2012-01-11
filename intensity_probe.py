#!/usr/bin/python
""" 
Intensity_Probe - given a directory of images and directory of 
corresponding cameras, click on a point in the presented image 
and have the intensities at that point in other images 
plotted to the left (histogrammed and by image number...)
"""
from boxm2_adaptor import *; 
from boxm2_scene_adaptor import *;
from vpgl_adaptor import *; 
from bbas_adaptor import *;
from vil_adaptor import *; 
from boxm2_tools_adaptor import *;
import scene_registry 
import random, os, sys;  
import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt;
from mpl_toolkits.mplot3d import axes3d
import numpy;
from numpy import arange, sin, pi , cos, arctan2, arccos
if matplotlib.get_backend() is not 'TkAgg': matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import *
from matplotlib.figure import Figure
from  Tkinter import*
import Image,ImageTk, ImageDraw
import glob,math,random
from optparse import OptionParser

####################################################### 
# handle inputs                                       #
#scene is given as first arg, figure out paths        #
parser = OptionParser()
parser.add_option("-s", "--scene", action="store", type="string", dest="scene", default="", help="specify scene name")
parser.add_option("-x", "--xmlfile", action="store", type="string", dest="xml", default="model/uscene.xml", help="scene.xml file name (model/uscene.xml, model_fixed/scene.xml, rscene.xml)")
parser.add_option("-g", "--gpu",   action="store", type="string", dest="gpu",   default="gpu1", help="specify gpu (gpu0, gpu1, etc)")
parser.add_option("-i", "--image", action="store", type="string", dest="image", default="", help="specify which image or directory to use")
parser.add_option("-c", "--camera", action="store", type="string", dest="camera", default="", help="specify corresponding camera or directory to use")
(options, args) = parser.parse_args()
print options
print args

############################################
# Create Scene
scene_root = scene_registry.scene_root( options.scene ); #
xmlPath = scene_root + "/" + options.xml
if not os.path.exists(xmlPath):
  print "Cannot find file: ", xmlPath
  sys.exit(-1) 
scene = boxm2_scene_adaptor(xmlPath, options.gpu);  

############################################
#search a bit for camera and image 
defImg = scene_root + "/nvm_out/imgs/"
defCam = scene_root + "/nvm_out/cams_krt/"
if os.path.exists(options.image) and os.path.exists(options.camera): 
  imageDir = options.image
  camDir = options.camera
elif os.path.exists(defImg) and os.path.exists(defCam):
  imageDir = defImg
  camDir = defCam
else:
  print "Can't find default image/cam dirs: ", defImg, defCam
  sys.exit(-1)
print "Image Directory: ", imageDir
imgList = glob.glob(imageDir + "/*")
camList = glob.glob(camDir + "/*.txt")
imgList.sort()
camList.sort()
assert(len(imgList) == len(camList))
assert(len(imgList) > 0) 


""" ImageFrame
Helper class keeps track of objects associated with an image frame 
"""
class ImageFrame:

  def __init__(self, frame=None, label=None, labString=None, currImg=0, row=0, col=0, label_image=None, image=None, tkpi=None):
    self.frame = frame
    self.label = label
    self.labString = labString
    self.label_image = label_image 
    self.currImg = currImg 
    self.row = row
    self.col = col 
    self.image = image 
    self.tkpi = tkpi
    self.lastClick = None

  
""" Application
gui app takes in Tk, imglist and camlist
"""
suntheta= 0.325398;
sunphi  =0.495398;
class App:
    def __init__(self,master,imgList,camList):
        self.master = master; 
        self.master.title("3d Point Intensity Tool");
        
        #store imgs/cams
        self.imgList = imgList
        self.camList = camList

        #Once a 3d point is generated, it is stored here, 
        #and all image's UV points stored in allUVs
        self.point3d = None 
        self.allUVs = []
        
        #############################################
        #set up plot frame 
        firstImg = Image.open(imgList[0]);
        print "Image size: ", firstImg.size
        self.reduceFactor = max(firstImg.size[0]/640.0, firstImg.size[1]/480.0)
        self.ni = int(firstImg.size[0]/self.reduceFactor + .5) 
        self.nj = int(firstImg.size[1]/self.reduceFactor + .5)
        self.frame = Frame(self.master, height=self.nj, width=self.ni, bg='blue');
        self.frame.grid_propagate(0)
        self.frame.pack();
        self.frame.grid(row=0, column=0)    
        # place a graph somewhere here
        self.f = Figure(figsize=(5.0,5.0), dpi=100)
        self.a = self.f.add_subplot(311)
        self.a.set_xlabel("t")
        self.a.set_ylabel("Info")
        self.a.plot([0,1,2,3,4],[0,1,2,3,4])
        self.canvas = FigureCanvasTkAgg(self.f, self.frame)
        self.canvas.show()
        #self.canvas.mpl_connect('button_press_event', self.get_t);
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        #############################################
        #set up button frame 
        self.bFrame = Frame(self.master, height=self.nj, width=self.ni)
        self.bFrame.grid_propagate(0)
        self.bFrame.pack()
        self.bFrame.grid(row=1, column=0)
        #place a button to generate 3d point, and grab intensities from each image
        self.genButton = Button(self.bFrame, text="Generate Point", command=self.point_from_rays)
        self.genButton.pack(fill=BOTH, expand=1)
        #button to clear the points
        self.clearButton = Button(self.bFrame, text="Clear Points", command=self.clear_points)
        self.clearButton.pack()
        #label for std dev and mean
        self.stdLabel = StringVar()
        Label(self.bFrame, textvariable=self.stdLabel).pack()
        self.meanLabel = StringVar()
        Label(self.bFrame, textvariable=self.meanLabel).pack()
        #label for 3d point
        self.pointLabel = StringVar()
        Label(self.bFrame, textvariable=self.pointLabel).pack()

        ##############################################        
        #set up images frames (should be 4 or so images)
        self.frames = []
        self.numImageFrames = 4
        frCount = 0
        for i in range(2):
          for j in range(2):
            labString = StringVar()
            label = Label(self.master, textvariable=labString)
            frame1 = LabelFrame(self.master, labelwidget=label, height=self.nj, width=self.ni, bg='green')
            frame1.pack();
            frame1.grid_propagate(0)
            frame1.grid(row=i, column=j+1, sticky=NW)      
            
            currFrame = (len(self.imgList) / self.numImageFrames) * frCount
            imageFrame = ImageFrame(frame1, label, labString, currFrame, i, j);
            self.frames.append(imageFrame) 
            frCount += 1
                  
        #display the first frame 
        for iFrame in self.frames:
          self.displayImage(iFrame)      
        
        #start the gui
        master.mainloop();
        
    def point_from_rays(self):
      """generate point from frames with clicked pixels"""
      print "generating the 3d point from given clicked points"
      
      #gather cams and points clicked  
      uvs = []
      cams = []
      for iFrame in self.frames:
        if iFrame.lastClick : 
          uv = numpy.multiply(iFrame.lastClick,self.reduceFactor)
          uvs.append(uv)
          cam = load_perspective_camera(self.camList[iFrame.currImg])
          cams.append(cam)
      point = get_3d_from_cams(cams, uvs)
      self.point3d = point;
      self.pointLabel.set("3d Point: " + str(self.point3d))

      # project 3d point into each image, and gather intensities   
      values = []
      ims    = []
      for idx, img in enumerate(self.imgList):
        cam = load_perspective_camera(self.camList[idx])
        imgPoint = project_point(cam, point[0], point[1], point[2])
        imgPoint = numpy.divide(imgPoint, self.reduceFactor)
        self.allUVs.append(imgPoint)
        
        #grab float intensity value at this point 
        imgView,ni,nj = load_image(img)
        val = pixel(imgView, imgPoint)
        if val > 0.0:
          values.append(val)
          ims.append(idx)
          
        #cleanup
        remove_from_db([imgView, cam])
      
      #now that each image has a corresponding make sure the
      #point is displayed in each image
      #self.clear_points();
      #for iFrame in self.frames:
        #point = self.allUVs[iFrame.currImg];
        #self.drawBox(iFrame)

      #write mean/std of intensities 
      self.meanLabel.set("Mean: " + str(numpy.mean(values)) )
      self.stdLabel.set("Std Dev: " + str(numpy.std(values)) )
      #plot the intensities by image number      
      self.f.clf();
      self.a = self.f.add_subplot(311)
      self.a.set_xlabel("img #")
      self.a.set_ylabel("intensity")
      self.a.plot(ims, values)
      #plot the histogram of intensities by image number      
      pdf, bins, patches = plt.hist(values)
      self.b = self.f.add_subplot(313)
      self.b.set_xlabel("bin val")
      self.b.set_ylabel("freq")
      self.b.hist(values, 15, normed=1, facecolor="green" )
      self.canvas.show();
      
    def clear_points(self):
      """clear points in each iFrame"""
      print "clearing each frame of selected points"
      self.point_3d = None
      self.allUVs = []
      for iFrame in self.frames:
        iFrame.lastClick = None; 
        self.displayImage(iFrame)
      
    def displayImage(self, iFrame, img=None):
        """given a frame displays the current image """
        if not img:
          imgPath = self.imgList[iFrame.currImg]
          img = Image.open(imgPath); 
          if img.mode == "I;16":
            print "16 bit image, converting to 8 bit"
            img.mode = 'I'
            img = img.point(lambda i:i*(1./256.)).convert("RGB");
          img = img.resize((self.ni, self.nj))

        #iframe keeps track of its image
        iFrame.image = img
         
        #if point is generated, gotta draw squares first
        if self.point3d:
          point = self.allUVs[iFrame.currImg];
          self.drawBox(iFrame, point)
         
        # store photo image (probably not needed in iFrame)
        iFrame.tkpi = ImageTk.PhotoImage(img) 
        
        #update frames' label 
        iFrame.labString.set("img {0}".format(iFrame.currImg))
        
        #create new label image
        if iFrame.label_image :
          iFrame.label_image.destroy()
        iFrame.label_image = Label(iFrame.frame, image=iFrame.tkpi)
        iFrame.label_image.image = iFrame.tkpi
        iFrame.label_image.bind("<Button-1>", lambda event, arg=iFrame: self.runprobe(event, iFrame))
        iFrame.label_image.bind("<Button-3>", lambda event, arg=iFrame: self.nextImage(event, iFrame)) 
        iFrame.label_image.bind("<Button-2>", lambda event, arg=iFrame: self.prevImage(event, iFrame))
        iFrame.label_image.pack(side = LEFT);

    def nextImage(self, event, iFrame):
        currImg = 1 + iFrame.currImg 
        if currImg >= len(self.imgList):
          currImg = 0
        iFrame.currImg = currImg
        print "Displaying next image: ", self.imgList[currImg]
        self.displayImage(iFrame); 
    
    def prevImage(self, event, iFrame):
        currImg = iFrame.currImg - 1 
        if currImg < 0 :
          currImg = len(self.imgList)-1
        iFrame.currImg = currImg
        print "Displaying next image: ", self.imgList[currImg]
        self.displayImage(iFrame); 
    
    def runprobe(self,event,iFrame):
        print "Image clicked on frame ", iFrame.row, iFrame.col
        print "    at point", event.x, event.y, " = ", iFrame.image.getpixel( (event.x, event.y) )
        #store x,y clicked and draw 
        iFrame.lastClick = (event.x, event.y)
        self.drawBox(iFrame, iFrame.lastClick)
        self.displayImage(iFrame, iFrame.image)
        
    def drawBox(self, iFrame, point):
        draw = ImageDraw.Draw(iFrame.image)
        imSize = iFrame.image.size
        p1 = ( max(point[0]-5,0), max(point[1]-5,0) )
        p2 = ( min(point[0]+5,imSize[0]-1), min(point[1]+5, imSize[1]-1) )
        draw.rectangle([p1, p2],  fill="green")
        del draw

#        self.posx=event.x;
#        self.posy=event.y;
#        array2d=list();
#        xs=list();
#        ys=list();
#        zs=list();
#        len_array_1d, alpha_array_1d, vis_array_1d, tabs_array_1d, phongs_array_1d, nelems = scene.get_info_along_ray(cam,self.posx, self.posy, "boxm2_mog3_grey");
#        print "NELEMS ", nelems;
#        surface_p = list();
#        air_p = list();
#        air_p1 = list();
#        num_observations = list();
#        for i in range(0,len(len_array_1d)):
#            surface_p.append(phongs_array_1d[i*nelems+5]);
#            air_p.append(phongs_array_1d[i*nelems+6]);
#            num_observations.append(phongs_array_1d[i*nelems+7]);
#        print surface_p
#        print air_p
#        print air_p1
#        print num_observations

#        self.b = self.f.add_subplot(312)
#        self.b.set_xlabel("zs")
#        self.b.set_ylabel("Air p")
#        self.b.plot(tabs_array_1d,air_p);
#        self.b.plot(tabs_array_1d,vis_array_1d);


#        self.b = self.f.add_subplot(313)
#        self.b.set_xlabel("zs")
#        self.b.set_ylabel("Nobs")
#        self.b.plot(tabs_array_1d,num_observations);  
#        self.canvas.show();
#        
#    def get_t(self,event):
#        print " Get T is called!!!!!!!!!!!!"
#        self.t =event.xdata;
#        self.ty=event.ydata;        # clear the figure
#        print self.t;
#        self.point[0],self.point[1],self.point[2] = get_3d_from_depth(pcam,self.posx,self.posy,self.t);
#        print "3-d point  ", self.point[0], self.point[1], self.point[2];
#        self.get_intensities();
#    def get_intensities(self):
#        print " Get Intensities! is called!!!!!!!!!!!!"
#        thetas=list();
#        phis=list();
#        cam_exp = 0;
#        img_ids=range(0,255,10);
#        scene.query_cell_brdf(self.point, "cubic_model"); 

#        #create stream cache using image/type lists:
#        image_id_fname = "./image_list.txt";
#        fd = open(image_id_fname,"w");
#        print >>fd, len(img_ids);
#        for i in img_ids:
#            print >>fd, "img_%05d"%i;
#        fd.close();

#        type_id_fname = "./type_names_list.txt";
#        fd2 = open(type_id_fname,"w");
#        print >>fd2, 4;
#        print >>fd2, "aux0";
#        print >>fd2, "aux1";
#        print >>fd2, "aux2";
#        print >>fd2, "aux3";
#        fd2.close();
#        
#        # open the stream cache, this is a read-only cache
#        boxm2_batch.init_process("boxm2CreateStreamCacheProcess");
#        boxm2_batch.set_input_from_db(0,scene.scene);
#        boxm2_batch.set_input_string(1,type_id_fname);
#        boxm2_batch.set_input_string(2,image_id_fname);
#        boxm2_batch.set_input_float(3,3);
#        boxm2_batch.run_process();
#        (cache_id, cache_type) = boxm2_batch.commit_output(0);
#        strcache = dbvalue(cache_id, cache_type);

#        #get intensities/visibilities
#        intensities, visibilities = probe_intensities(scene.scene, scene.cpu_cache, strcache, self.point)

#        boxm2_batch.init_process("boxm2StreamCacheCloseFilesProcess");
#        boxm2_batch.set_input_from_db(0,strcache);
#        boxm2_batch.run_process();
#        image_id_fname = "./image_list.txt";
#        # write image identifiers to file
#        fd = open(image_id_fname,"w");
#        print >>fd, len(img_ids);
#        for i in img_ids:
#            print >>fd, "viewdir_%05d"%i;
#        fd.close();

#        # open the stream cache, this is a read-only cache
#        boxm2_batch.init_process("boxm2CreateStreamCacheProcess");
#        boxm2_batch.set_input_from_db(0,scene.scene);
#        boxm2_batch.set_input_string(1,type_id_fname);
#        boxm2_batch.set_input_string(2,image_id_fname);
#        boxm2_batch.set_input_float(3,3);
#        boxm2_batch.run_process();
#        (cache_id, cache_type) = boxm2_batch.commit_output(0);
#        strcache = dbvalue(cache_id, cache_type);

#        boxm2_batch.init_process("boxm2CppBatchProbeIntensitiesProcess");
#        boxm2_batch.set_input_from_db(0,scene.scene);
#        boxm2_batch.set_input_from_db(1,scene.cpu_cache);
#        boxm2_batch.set_input_from_db(2,strcache);
#        boxm2_batch.set_input_float(3,self.point[0]);
#        boxm2_batch.set_input_float(4,self.point[1]);
#        boxm2_batch.set_input_float(5,self.point[2]);
#        boxm2_batch.run_process();
#        (id,type) = boxm2_batch.commit_output(0);
#        xdir=boxm2_batch.get_bbas_1d_array_float(id);
#        (id,type) = boxm2_batch.commit_output(1);
#        ydir=boxm2_batch.get_bbas_1d_array_float(id);
#        (id,type) = boxm2_batch.commit_output(2);
#        zdir=boxm2_batch.get_bbas_1d_array_float(id);
#        phis =[];
#        for i in range(0, len(xdir)):
#          phis.append( arctan2(ydir[i],xdir[i]));
#          thetas.append(arccos(zdir[i]));

#        boxm2_batch.init_process("boxm2StreamCacheCloseFilesProcess");
#        boxm2_batch.set_input_from_db(0,strcache);
#        boxm2_batch.run_process();
#    
#        boxm2_batch.init_process("bradEstimateSynopticFunction1dProcess");
#        boxm2_batch.set_input_float_array(0,intensities);
#        boxm2_batch.set_input_float_array(1,visibilities);
#        boxm2_batch.set_input_float_array(2,thetas);
#        boxm2_batch.set_input_float_array(3,phis);
#        boxm2_batch.set_input_bool(4,1);
#        boxm2_batch.run_process();
#        (id,type) = boxm2_batch.commit_output(0);
#        fitted_intensities=boxm2_batch.get_bbas_1d_array_float(id);
#        (id,type) = boxm2_batch.commit_output(1);
#        surf_prob_density=boxm2_batch.get_output_float(id);
#      
#        
#        boxm2_batch.init_process("bradEstimateEmptyProcess");
#        boxm2_batch.set_input_float_array(0,intensities);
#        boxm2_batch.set_input_float_array(1,visibilities);
#        boxm2_batch.run_process();
#        (id,type) = boxm2_batch.commit_output(0);
#        air_prob_density=boxm2_batch.get_output_float(id);
#        print "surf_prob_density ", surf_prob_density, "air_prob_density ", air_prob_density
#      
#        #fig = plt.figure(2)
#        #fig.clf();
#        #ax = fig.gca(projection='3d')
#      
#        select_intensities=list();
#        select_intensities_img=list();
#        select_fitted_intensities=list();
#        select_visibilities=list();
#        select_indices=list();
#        print len(thetas), len (intensities);
#        for pindex in range(0,len(intensities)):
#          r=intensities[pindex];
#          theta=thetas[pindex];
#          phi=phis[pindex];
#          r1=fitted_intensities[pindex];
#          if(intensities[pindex]<0.0):
#            visibilities[pindex]=0.0;
#          if(visibilities[pindex]>0.0 ):
#            vispl=visibilities[pindex];
#            #ax.plot([0,r*sin(theta)*cos(phi)],[0,r*sin(theta)*sin(phi)],[0,r*cos(theta)], color='b');
#            #ax.scatter([r1*sin(theta)*cos(phi)],[r1*sin(theta)*sin(phi)],[r1*cos(theta)], color='g');
#            #ax.scatter([vispl*sin(theta)*cos(phi)],[vispl*sin(theta)*sin(phi)],[vispl*cos(theta)], color='r');
#            print intensities[pindex],  phis[pindex], visibilities[pindex];
#            select_intensities.append(r);
#            select_visibilities.append(vispl);
#            select_indices.append(pindex);
#            select_fitted_intensities.append(r1);
#            #select_intensities_img.append(intensities_img[pindex]);
#          #ax.plot([0,sin(suntheta)*cos(sunphi)],[0,sin(suntheta)*sin(sunphi)],[0,cos(suntheta)], color='r');
#          #ax.plot([0,0],[0,0],[0,1], color='k');
#          #ax.set_xlim3d(-1,1);ax.set_ylim3d(-1,1);ax.set_zlim3d(0,1);
#      #plt.show();
#        fig_hist=plt.figure(3);
#        plt.xlabel("ViewPoints")
#        plt.ylabel("Intensities")
#        plt.plot(select_indices,select_intensities,'r*-');
#        plt.plot(select_indices,select_fitted_intensities,'g.-');
#        plt.ylim((0,1));
#        plt.plot(select_indices,select_visibilities,'bo-');
#      #plt.plot(select_indices,select_intensities_img,'ko-');
#        #plt.legend( ('Intensities Observed', 'Phong\'s Model','Visibilities'), loc='lower left');    
#        plt.show();
#        
#instantiate Tk root, and make App
root = Tk();
app = App(root, imgList, camList);

