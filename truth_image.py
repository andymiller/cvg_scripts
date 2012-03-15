#!/usr/bin/python
""" 
truth_image - a tool to help create an image mask or ground truth an image
"""
import os, sys;  
import matplotlib
from matplotlib.backends.backend_tkagg import *
from matplotlib.figure import Figure
#matplotlib.use('TkAgg')
if matplotlib.get_backend() is not 'TkAgg': 
  matplotlib.use('TkAgg')

import matplotlib.pyplot as plt;
from mpl_toolkits.mplot3d import axes3d
import numpy;
#from numpy import arange, sin, pi , cos, arctan2, arccos
from  Tkinter import*
import Image, ImageTk, ImageDraw
#import glob,math,random
from optparse import OptionParser

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
class App:
    def __init__(self,master,initImg):
        self.master = master; 
        self.master.title("Image Ground Truthing Tool");
        
        #initialize image
        self.image = initImg; 
        
        ############################################
        #set up left frame and classes list
        self.leftFrame = Frame(self.master, width=200, bg='blue');
        self.leftFrame.grid_propagate(0)
        self.leftFrame.pack();
        self.leftFrame.grid(row=0, column=0)    
        
        self.classFrame = Frame(self.leftFrame, width=200, bg='red')
        self.classes = ["water"]
        self.classLabels = []
        for c in self.classes:
          clab = Label(self.classFrame, text=c)
          clab.pack()
          self.classLabels.append(clab)
        self.classFrame.pack()

        #############################################
        #set up button frame 
        self.bFrame = Frame(self.leftFrame, width=200)
        self.bFrame.pack()
        #place a button to generate 3d point, and grab intensities from each image
        self.genButton = Button(self.bFrame, text="create mask", command=self.create_mask)
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
        # set up image display 
        firstImg = Image.open(self.image);
        tkImg = ImageTk.PhotoImage(firstImg)
        w = Label(self.master, image=tkImg)
        w.photo = tkImg
        w.pack()
        w.grid(row=0, column=1)
        #iFrame.tkpi = ImageTk.PhotoImage(img) 
        #frame1.label_image = Label(frame1, 
        #create new label image
        #if iFrame.label_image :
        #  iFrame.label_image.destroy()
        #iFrame.label_image = Label(iFrame.frame, image=iFrame.tkpi)
        #iFrame.label_image.image = iFrame.tkpi
        #iFrame.label_image.bind("<Button-1>", lambda event, arg=iFrame: self.runprobe(event, iFrame))
        #iFrame.label_image.bind("<Button-3>", lambda event, arg=iFrame: self.nextImage(event, iFrame)) 
        #iFrame.label_image.bind("<Button-2>", lambda event, arg=iFrame: self.prevImage(event, iFrame))
        #iFrame.label_image.pack(side = LEFT);

        #display the first frame 
        #self.displayImage(iFrame)      
        
        #self.frames = []
        #self.numImageFrames = 4
        #frCount = 0
        #for i in range(2):
        #  for j in range(2):
        #    labString = StringVar()
        #    label = Label(self.master, textvariable=labString)
        #    frame1 = LabelFrame(self.master, labelwidget=label, height=self.nj, width=self.ni, bg='green')
        #    frame1.pack();
        #    frame1.grid_propagate(0)
        #    frame1.grid(row=i, column=j+1, sticky=NW)      
        #    
        #    currFrame = (len(self.imgList) / self.numImageFrames) * frCount
        #    imageFrame = ImageFrame(frame1, label, labString, currFrame, i, j);
        #    self.frames.append(imageFrame) 
        #    frCount += 1
        #          
        ##display the first frame 
        #for iFrame in self.frames:
        #  self.displayImage(iFrame)      
        
        #start the gui
        master.mainloop();
    
    def create_mask(self):
      print "CREATING MASK!"


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


#MAIN
if __name__ == "__main__":
  # handle inputs
  parser = OptionParser()
  parser.add_option("-i", "--image", action="store", type="string", dest="image", default="", help="specify image to start with (optional)")
  (options, args) = parser.parse_args()

  #instantiate Tk root, and make App
  root = Tk();
  app = App(root, options.image)


