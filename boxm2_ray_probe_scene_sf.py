from boxm2_adaptor import *; 
from boxm2_scene_adaptor import *;
from vpgl_adaptor import *; 
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
import Image,ImageTk
import glob,math,random
from optparse import OptionParser

####################################################### 
# handle inputs                                       #
#scene is given as first arg, figure out paths        #
parser = OptionParser()
parser.add_option("-s", "--scene", action="store", type="string", dest="scene", default="", help="specify scene name")
parser.add_option("-x", "--xmlfile", action="store", type="string", dest="xml", default="model/uscene.xml", help="scene.xml file name (model/uscene.xml, model_fixed/scene.xml, rscene.xml)")
parser.add_option("-g", "--gpu",   action="store", type="string", dest="gpu",   default="gpu1", help="specify gpu (gpu0, gpu1, etc)")
parser.add_option("-i", "--image", action="store", type="string", dest="image", default="", help="specify which image to use")
parser.add_option("-c", "--camera", action="store", type="string", dest="camera", default="", help="specify corresponding camera to use")
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
imageDir = scene_root + "/nvm_out/imgs/"
if options.image == "" and os.path.exists(imageDir):
  print "Using first image, guessing dir: ", imageDir
  imGlob = glob.glob(imageDir + "/*")
  if len(imGlob) > 0 :  
    image_filename  = imGlob[0]
  else:
    print "Can't find default image directory"
    sys.exit(-1)
elif options.image != "":
  print "Can't find default image directory"
  sys.exit(-1)
else:
  image_filename = options.image;
print "Image filename: ", image_filename
  
imgNumber, ext = os.path.splitext(os.path.basename(image_filename))
if options.camera == "":
  camGuess = scene_root + "/nvm_out/cams_krt/" + imgNumber + "_cam.txt"
  if os.path.exists(camGuess):
    cam_name = camGuess
  else:
    print "Can't find camera: ", options.camera, " or guess, ", camGuess
    sys.exit(-1)
elif os.path.exists(options.camera) :
  cam_name  = options.camera
else:
  print "Can't find camera: ", options.camera, " or default cam directory"
  sys.exit(-1)
 
#Load camera 
pcam = load_perspective_camera(cam_name); 
img, ni, nj = load_image(image_filename); 
cam  = persp2gen(pcam,ni,nj);

suntheta= 0.325398;
sunphi  =0.495398;
class App:
    def __init__(self,master,image_path):
        self.point=[0,0,0];
        master.title("3d Point");
        self.image1 = Image.open(image_path);            
        self.tkpi = ImageTk.PhotoImage(self.image1)
        self.frame = Frame(master, height= self.image1.size[1], width=self.image1.size[0]);
        self.frame.grid_propagate(0)
        self.frame.pack();
        self.frame.grid(row=0, column=0, sticky=NW)     

        # place a graph somewhere here
        self.f = Figure(figsize=(6.4,7.2), dpi=100)
        self.a = self.f.add_subplot(311)
        self.a.set_xlabel("t")
        self.a.set_ylabel("Info")
        self.a.plot([0,1,2,3,4],[0,1,2,3,4])

        self.canvas = FigureCanvasTkAgg(self.f, self.frame)
        self.canvas.show()
        self.canvas.mpl_connect('button_press_event', self.get_t);
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        self.frame1 = Frame(master, height= self.image1.size[1], width=2*self.image1.size[0], bg='red')
        self.frame1.pack();
        self.frame1.grid_propagate(0)
        self.frame1.grid(row=0, column=1, sticky=NW)      
        self.label_image = Label(self.frame1, image=self.tkpi)
        self.label_image.pack(side = LEFT);
        self.label_image.bind("<Button-1>", self.runprobe); 
        master.mainloop();
        
        
    def get_t(self,event):
        self.t =event.xdata;
        self.ty=event.ydata;        # clear the figure
        print self.t;
        self.point[0],self.point[1],self.point[2] = get_3d_from_depth(pcam,self.posx,self.posy,self.t);
        print "3-d point  ", self.point[0], self.point[1], self.point[2];
        # self.point[0] = 0.03285;#0.0694333;#0.0908;
        # self.point[1] = 0.08402;#0.0636396;#-0.0068;
        # self.point[2] = 0.181359;#0.150683; #0.13447;
        self.get_intensities();
    
    def runprobe(self,event):
        self.posx=event.x;
        self.posy=event.y;
        array2d=list();
        xs=list();
        ys=list();
        zs=list();
        len_array_1d, alpha_array_1d, vis_array_1d, tabs_array_1d, phongs_array_1d, nelems = scene.get_info_along_ray(cam,self.posx, self.posy, "boxm2_mog3_grey");
        print "NELEMS ", nelems;
        surface_p = list();
        air_p = list();
        air_p1 = list();
        num_observations = list();
        for i in range(0,len(len_array_1d)):
            surface_p.append(phongs_array_1d[i*nelems+5]);
            air_p.append(phongs_array_1d[i*nelems+6]);
            num_observations.append(phongs_array_1d[i*nelems+7]);

        self.f.clf();
        self.a = self.f.add_subplot(311)
        self.a.set_xlabel("zs")
        self.a.set_ylabel("Cubic p")
        self.a.plot(tabs_array_1d,surface_p);
        self.a.plot(tabs_array_1d,vis_array_1d);

        self.b = self.f.add_subplot(312)
        self.b.set_xlabel("zs")
        self.b.set_ylabel("Air p")
        self.b.plot(tabs_array_1d,air_p);
        self.b.plot(tabs_array_1d,vis_array_1d);


        self.b = self.f.add_subplot(313)
        self.b.set_xlabel("zs")
        self.b.set_ylabel("Nobs")
        self.b.plot(tabs_array_1d,num_observations);  
        self.canvas.show();
        
    def get_intensities(self):
        thetas=list();
        phis=list();
        cam_exp = 0;
        img_ids=range(0,255,10);
        scene.query_cell_brdf(self.point, "cubic_model"); 

        #create stream cache using image/type lists:
        image_id_fname = "./image_list.txt";
        fd = open(image_id_fname,"w");
        print >>fd, len(img_ids);
        for i in img_ids:
            print >>fd, "img_%05d"%i;
        fd.close();

        type_id_fname = "./type_names_list.txt";
        fd2 = open(type_id_fname,"w");
        print >>fd2, 4;
        print >>fd2, "aux0";
        print >>fd2, "aux1";
        print >>fd2, "aux2";
        print >>fd2, "aux3";
        fd2.close();
        
        # open the stream cache, this is a read-only cache
        boxm2_batch.init_process("boxm2CreateStreamCacheProcess");
        boxm2_batch.set_input_from_db(0,scene.scene);
        boxm2_batch.set_input_string(1,type_id_fname);
        boxm2_batch.set_input_string(2,image_id_fname);
        boxm2_batch.set_input_float(3,3);
        boxm2_batch.run_process();
        (cache_id, cache_type) = boxm2_batch.commit_output(0);
        strcache = dbvalue(cache_id, cache_type);

        #get intensities/visibilities
        intensities, visibilities = probe_intensities(scene.scene, scene.cpu_cache, strcache, self.point)

        boxm2_batch.init_process("boxm2StreamCacheCloseFilesProcess");
        boxm2_batch.set_input_from_db(0,strcache);
        boxm2_batch.run_process();
        image_id_fname = "./image_list.txt";
        # write image identifiers to file
        fd = open(image_id_fname,"w");
        print >>fd, len(img_ids);
        for i in img_ids:
            print >>fd, "viewdir_%05d"%i;
        fd.close();

        # open the stream cache, this is a read-only cache
        boxm2_batch.init_process("boxm2CreateStreamCacheProcess");
        boxm2_batch.set_input_from_db(0,scene.scene);
        boxm2_batch.set_input_string(1,type_id_fname);
        boxm2_batch.set_input_string(2,image_id_fname);
        boxm2_batch.set_input_float(3,3);
        boxm2_batch.run_process();
        (cache_id, cache_type) = boxm2_batch.commit_output(0);
        strcache = dbvalue(cache_id, cache_type);

        boxm2_batch.init_process("boxm2CppBatchProbeIntensitiesProcess");
        boxm2_batch.set_input_from_db(0,scene.scene);
        boxm2_batch.set_input_from_db(1,scene.cpu_cache);
        boxm2_batch.set_input_from_db(2,strcache);
        boxm2_batch.set_input_float(3,self.point[0]);
        boxm2_batch.set_input_float(4,self.point[1]);
        boxm2_batch.set_input_float(5,self.point[2]);
        boxm2_batch.run_process();
        (id,type) = boxm2_batch.commit_output(0);
        xdir=boxm2_batch.get_bbas_1d_array_float(id);
        (id,type) = boxm2_batch.commit_output(1);
        ydir=boxm2_batch.get_bbas_1d_array_float(id);
        (id,type) = boxm2_batch.commit_output(2);
        zdir=boxm2_batch.get_bbas_1d_array_float(id);
        phis =[];
        for i in range(0, len(xdir)):
          phis.append( arctan2(ydir[i],xdir[i]));
          thetas.append(arccos(zdir[i]));

        boxm2_batch.init_process("boxm2StreamCacheCloseFilesProcess");
        boxm2_batch.set_input_from_db(0,strcache);
        boxm2_batch.run_process();
    
        boxm2_batch.init_process("bradEstimateSynopticFunction1dProcess");
        boxm2_batch.set_input_float_array(0,intensities);
        boxm2_batch.set_input_float_array(1,visibilities);
        boxm2_batch.set_input_float_array(2,thetas);
        boxm2_batch.set_input_float_array(3,phis);
        boxm2_batch.set_input_bool(4,1);
        boxm2_batch.run_process();
        (id,type) = boxm2_batch.commit_output(0);
        fitted_intensities=boxm2_batch.get_bbas_1d_array_float(id);
        (id,type) = boxm2_batch.commit_output(1);
        surf_prob_density=boxm2_batch.get_output_float(id);
      
        
        boxm2_batch.init_process("bradEstimateEmptyProcess");
        boxm2_batch.set_input_float_array(0,intensities);
        boxm2_batch.set_input_float_array(1,visibilities);
        boxm2_batch.run_process();
        (id,type) = boxm2_batch.commit_output(0);
        air_prob_density=boxm2_batch.get_output_float(id);
        print "surf_prob_density ", surf_prob_density, "air_prob_density ", air_prob_density
      
        #fig = plt.figure(2)
        #fig.clf();
        #ax = fig.gca(projection='3d')
      
        select_intensities=list();
        select_intensities_img=list();
        select_fitted_intensities=list();
        select_visibilities=list();
        select_indices=list();
        print len(thetas), len (intensities);
        for pindex in range(0,len(intensities)):
          r=intensities[pindex];
          theta=thetas[pindex];
          phi=phis[pindex];
          r1=fitted_intensities[pindex];
          if(intensities[pindex]<0.0):
            visibilities[pindex]=0.0;
          if(visibilities[pindex]>0.0 ):
            vispl=visibilities[pindex];
            #ax.plot([0,r*sin(theta)*cos(phi)],[0,r*sin(theta)*sin(phi)],[0,r*cos(theta)], color='b');
            #ax.scatter([r1*sin(theta)*cos(phi)],[r1*sin(theta)*sin(phi)],[r1*cos(theta)], color='g');
            #ax.scatter([vispl*sin(theta)*cos(phi)],[vispl*sin(theta)*sin(phi)],[vispl*cos(theta)], color='r');
            print intensities[pindex],  phis[pindex], visibilities[pindex];
            select_intensities.append(r);
            select_visibilities.append(vispl);
            select_indices.append(pindex);
            select_fitted_intensities.append(r1);
            #select_intensities_img.append(intensities_img[pindex]);
          #ax.plot([0,sin(suntheta)*cos(sunphi)],[0,sin(suntheta)*sin(sunphi)],[0,cos(suntheta)], color='r');
          #ax.plot([0,0],[0,0],[0,1], color='k');
          #ax.set_xlim3d(-1,1);ax.set_ylim3d(-1,1);ax.set_zlim3d(0,1);
      #plt.show();
        fig_hist=plt.figure(3);
        plt.xlabel("ViewPoints")
        plt.ylabel("Intensities")
        plt.plot(select_indices,select_intensities,'r*-');
        plt.plot(select_indices,select_fitted_intensities,'g.-');
        plt.ylim((0,1));
        plt.plot(select_indices,select_visibilities,'bo-');
      #plt.plot(select_indices,select_intensities_img,'ko-');
        #plt.legend( ('Intensities Observed', 'Phong\'s Model','Visibilities'), loc='lower left');    
        plt.show();
root = Tk();
app=App(root,image_filename);

