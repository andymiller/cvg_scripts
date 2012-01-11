import os, sys, struct, array
from os.path import basename, splitext; 
import Tkinter
import Image, ImageTk

###########################################
#check args
###########################################
if len(sys.argv) < 2:
  print "First argument should be raw file!"
  sys.exit(-1)
rawFile = sys.argv[1]; 

SAVE_IMAGES = False
if len(sys.argv) > 2:
  if sys.argv[2] == "save":
    SAVE_IMAGES = True
    
INTERVAL= 6
MAX_IMG = 1300

###########################################
# this will cause mainloop to unblock.
###########################################
def button_click_exit_mainloop (event):
    event.widget.quit() 

###########################################
#setup Tk
###########################################
root = Tkinter.Tk()
root.bind("<Button>", button_click_exit_mainloop)
root.geometry('+%d+%d' % (100,100))

###########################################
#open raw file, read header info
###########################################
fin = open(rawFile, "rb")
ni,nj = struct.unpack('ii', fin.read(8))
pixelSize = struct.unpack('i', fin.read(4))[0]
numFrames = struct.unpack('q', fin.read(8))[0];
print "Image Size: ",ni,',',nj
print "PixSize: ", pixelSize, "bits"
print "numFrame:", numFrames
if MAX_IMG < 0 : 
  MAX_IMG = numFrames

###########################################
#calc image size (in bytes), figure out pixeltypes
###########################################
imgSize = pixelSize*ni*nj/8
if pixelSize==16 :
  pixelMode = "L"
  arrayMode = "H"
elif pixelSize==24 :
  pixelMode = "RGB"
  arrayMode = "B"
 
###########################################
#iterater over images
###########################################
old_label_image = None
for idx in range(0, MAX_IMG, INTERVAL):
  try: 
    imgStart = 20 + (imgSize+8)*idx
    fin.seek(imgStart)
    img = array.array(arrayMode)
    img.fromfile(fin, imgSize)
    print "ITEM SIZE: ", img.itemsize
    
    #convert from uint16
    if pixelSize==16:
      bimg = array.array('B')
      bimg.fromstring(img.tostring())
      img = bimg
      
    im = Image.frombuffer(pixelMode, (ni,nj), img, "raw", pixelMode, 0, 0)
    time = struct.unpack('q', fin.read(8))[0]
    
    #if saving images, don't show them
    if SAVE_IMAGES:
      if pixelSize==24: 
        ext=".png" 
      else: 
        ext=".tiff"
      imgName = "eo_%05d_time_%010d.png" % (idx, time)
      im.save(imgName)
      print "Saved image ", idx, " of ", MAX_IMG
      
    else: #show image in tk window    
      im = im.resize((ni/4, nj/4))
      root.geometry('%dx%d' % (im.size[0],im.size[1]))
      tkpi = ImageTk.PhotoImage(im)
      label_image = Tkinter.Label(root, image=tkpi)
      label_image.place(x=0,y=0,width=im.size[0],height=im.size[1])
      
      name = "img " + str(idx) + " of " + str(numFrames) + " time:" + str(imgTime)
      root.title(name)
      if old_label_image is not None:
        old_label_image.destroy()
      old_label_image = label_image
      root.mainloop()
  except:
    print "Unexpected error:", sys.exc_info()[0]
    finself.close()

#close raw file
fin.close()


