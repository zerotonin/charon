# -*- coding: utf-8 -*-
"""
 ▄████▄   ██░ ██  ▄▄▄       ██▀███   ▒█████   ███▄    █ 
▒██▀ ▀█  ▓██░ ██▒▒████▄    ▓██ ▒ ██▒▒██▒  ██▒ ██ ▀█   █ 
▒▓█    ▄ ▒██▀▀██░▒██  ▀█▄  ▓██ ░▄█ ▒▒██░  ██▒▓██  ▀█ ██▒
▒▓▓▄ ▄██▒░▓█ ░██ ░██▄▄▄▄██ ▒██▀▀█▄  ▒██   ██░▓██▒  ▐▌██▒
▒ ▓███▀ ░░▓█▒░██▓ ▓█   ▓██▒░██▓ ▒██▒░ ████▓▒░▒██░   ▓██░
░ ░▒ ▒  ░ ▒ ░░▒░▒ ▒▒   ▓▒█░░ ▒▓ ░▒▓░░ ▒░▒░▒░ ░ ▒░   ▒ ▒ 
  ░  ▒    ▒ ░▒░ ░  ▒   ▒▒ ░  ░▒ ░ ▒░  ░ ▒ ▒░ ░ ░░   ░ ▒░
░         ░  ░░ ░  ░   ▒     ░░   ░ ░ ░ ░ ▒     ░   ░ ░ 
░ ░       ░  ░  ░      ░  ░   ░         ░ ░           ░ 
░                                                       

@author: bgeurten
"""

import os,glob,cv2,sys
import pandas as pd
import numpy as np
import tensorflow as tf
from tqdm import tqdm
from zipfile import ZipFile, ZIP_DEFLATED
# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("/home/bgeurten/tensorFlowModels/research/object_detection")

# Import utilites
from utils import label_map_util
from utils import visualization_utils as vis_util
from PIL import Image


class charon:
    def __init__(self,cellType='locustNeuron'):

        self.setCellTypeAI(cellType)


    def initModel(self,
                 NUM_CLASSES      = 2, 
                 MODEL_NAME       = 'interference_graph3',
                 DETECTION_THRESH = 0.75,
                 OBJECT_DET_DIR   = '/home/bgeurten/tensorFlowModels/research/object_detection',
                 OUTPUT_DIR       = '/media/dataSSD/cellDetector/done',
                 ZIP_DIR          = '/media/dataSSD/cellDetector/zips',
                 WORK_DIR         = '/media/dataSSD/cellDetector/analysing',
                 PATH_TO_LABELS   = '/home/bgeurten/tensorFlowModels/research/object_detection/training_cellDetectorv02/'):
        # Name of the directory containing the object detection module we're using
        self.MODEL_NAME       = MODEL_NAME
        self.DETECTION_THRESH = DETECTION_THRESH
        self.OBJECT_DET_DIR   = OBJECT_DET_DIR

        # Path to frozen detection graph .pb file, which contains the model that is used
        # for object detection.
        self.PATH_TO_CKPT = os.path.join(self.OBJECT_DET_DIR,MODEL_NAME,'frozen_inference_graph.pb')

        # Path to label map file
        self.PATH_TO_LABELS = os.path.join(self.PATH_TO_LABELS,'labelmap.pbtxt')


        # Number of classes the object detector can identify
        self.NUM_CLASSES = NUM_CLASSES

        # Load the label map.
        # Label maps map indices to category names, so that when our convolution
        # network predicts `5`, we know that this corresponds to `king`.
        # Here we use internal utility functions, but anything that returns a
        # dictionary mapping integers to appropriate string labels would be fine
        self.label_map = label_map_util.load_labelmap(self.PATH_TO_LABELS)
        self.categories = label_map_util.convert_label_map_to_categories(self.label_map, max_num_classes=self.NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(self.categories)
        self.fileList = list()
        self.OUTPUT_DIR = OUTPUT_DIR
        self.ZIP_DIR = ZIP_DIR
        self.WORK_DIR = WORK_DIR
        self.sess = None

    def setCellTypeAI(self,cellType):

        if cellType == 'locustNeuron':
            self.initModel()
        elif cellType == 'locustHaemo':
            self.initModel(2, #NUM_CLASSES     
                          'haemoCellGraph',#MODEL_NAME      
                          0.75,#DETECTION_THRESH
                          '/home/bgeurten/tensorFlowModels/research/object_detection',#OBJECT_DET_DIR  
                          '/media/dataSSD/cellDetector/done',#OUTPUT_DIR      
                          '/media/dataSSD/cellDetector/zips',#ZIP_DIR         
                          '/media/dataSSD/cellDetector/analysing',#WORK_DIR        
                          '/home/bgeurten/tensorFlowModels/research/object_detection/haemoCellGraph')#PATH_TO_LABELS  
        else:
            print('There is no model for celltype: ' +str(cellType))

        

    def getImagePos_search(self,path,ext):
        
        imgList = []
        # r=root, d=directories, f = files
        for r, d, f in os.walk(path):
            for file in f:
                if ext in file:
                    imgList.append(os.path.join(r, file))
        imgList.sort()
        return imgList
    
        

    def getImagePos_readTXT(self,fileName):
        return [line.rstrip('\n') for line in open(fileName)]
    
    def setUp_tensorFlow(self):
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            self.sess = tf.Session(graph=detection_graph)

        # Define input and output tensors (i.e. data) for the object detection classifier

        # Input tensor is the image
        self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

        # Output tensors are the detection boxes, scores, and classes
        # Each box represents a part of the image where a particular object was detected
        self.detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

        # Each score represents level of confidence for each of the objects.
        # The score is shown on the result image, together with the class label.
        self.detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

        # Number of objects detected
        self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')

        #label dict shortcuts for human readable outputs
        self.labelDict     = label_map_util.get_label_map_dict(self.PATH_TO_LABELS)
        self.labelDictInv  = {y:x for x,y in self.labelDict.items()}

    def setUp_XLSwriter(self,subfolder,fileName):
        xlsPos = os.path.join(self.OUTPUT_DIR,subfolder)
        xlsPos = os.path.join(xlsPos,fileName)
        self.writer = pd.ExcelWriter(xlsPos, engine='xlsxwriter')

    def analyseMovie(self,moviePos,pathOut,xlsFilename):
        # Load the Tensorflow model into memory if this was not done before in self.runExperiment().
        if self.sess == None:
            self.setUp_tensorFlow()
        #set up xlsx writer
        self.setUp_XLSwriter(os.path.dirname(xlsFilename),os.path.basename(xlsFilename))

        # video reader enabled
        cap = cv2.VideoCapture("/media/bgeurten/HSMovieKrissy/Group of flies(around 30)/30_09_19/2019-09-30__16_55_47.avi")
        #fps 
        fps = round(cap.get(cv2.CAP_PROP_FPS))
        # read fideo frame 
        ret, image = cap.read()    
        height, width, layers = image.shape
        im_size = (width,height)
        out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'DIVX'), fps, im_size)
        c = 0
        while ret == True:
            # expand image
            image_expanded = np.expand_dims(image, axis=0)      # Path to image

             # Perform the actual detection by running the model with the image as input
            (boxes, scores, classes, num) = self.sess.run([self.detection_boxes, 
                                                           self.detection_scores, 
                                                           self.detection_classes, 
                                                           self.num_detections],
                                                           feed_dict={self.image_tensor: image_expanded})

            # get all scores above above threshold
            idx       = scores >= self.DETECTION_THRESH
            box_OUT   = boxes[idx]
            score_OUT = scores[idx]
            class_OUT = classes[idx]
            #human readable classes
            class_STR_OUT = [self.labelDictInv[a] for a in class_OUT]
   
            data_OUT = [class_STR_OUT, score_OUT.tolist(), box_OUT.tolist()]
            data_OUT = list(map(list, zip(*data_OUT)))
            df = pd.DataFrame(data_OUT, columns = ['Type', 'Score','Box']) 
            df.to_excel(self.writer, sheet_name='frame ' + str(c))
            
            # Draw the results of the detection (aka 'visulaize the results')

            vis_util.visualize_boxes_and_labels_on_image_array(
                image,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                self.category_index,
                use_normalized_coordinates=True,
                line_thickness=4,
                min_score_thresh=self.DETECTION_THRESH,
                track_ids=np.array(range(len(scores[0])),dtype=int),
                max_boxes_to_draw= 500)
            # write out image
            out.write(image)
            # frame Counter 
            c+=1
            # read fideo frame 
            ret, image = cap.read()    

            
        out.release()
        self.writer.save()

    def analyseImageList(self,subfolder,xlsFileName):
        # Load the Tensorflow model into memory if this was not done before in self.runExperiment().
        if self.sess == None:
            self.setUp_tensorFlow()

        self.setUp_XLSwriter(subfolder,xlsFileName)
        countCells  = np.zeros([len(self.imgList),self.NUM_CLASSES],dtype=int)
        fileNameList = list()
        imageI = 0
        for IMAGE_NAME in tqdm(self.imgList,desc='analysing ' + xlsFileName[0:-5]):
  
            # Load image using OpenCV and
            # expand image dimensions to have shape: [1, None, None, 3]
            # i.e. a single-column array, where each item in the column has the pixel RGB value
            image = cv2.imread(IMAGE_NAME)
            image_expanded = np.expand_dims(image, axis=0)      # Path to image
            (outPath,fileName) = os.path.split(IMAGE_NAME)
            fileNameList.append(fileName)

            # Perform the actual detection by running the model with the image as input
            (boxes, scores, classes, num) = self.sess.run([self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],feed_dict={self.image_tensor: image_expanded})

            # get all scores above above threshold
            idx       = scores >= self.DETECTION_THRESH
            box_OUT   = boxes[idx]
            score_OUT = scores[idx]
            class_OUT = classes[idx]
            #human readable classes
            class_STR_OUT = [self.labelDictInv[a] for a in class_OUT]
   
            #sumarize in image
            c = 0
            for key in self.labelDict:
                countCells[imageI,c] = class_STR_OUT.count(key)
                c+=1    

            data_OUT = [class_STR_OUT, score_OUT.tolist(), box_OUT.tolist()]
            data_OUT = list(map(list, zip(*data_OUT)))
            df = pd.DataFrame(data_OUT, columns = ['Type', 'Score','Box']) 
            df.to_excel(self.writer, sheet_name=fileName)

            imageI+=1
            # Draw the results of the detection (aka 'visulaize the results')

            vis_util.visualize_boxes_and_labels_on_image_array(
                image,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                self.category_index,
                use_normalized_coordinates=True,
                line_thickness=4,
                min_score_thresh=self.DETECTION_THRESH,
                track_ids=np.array(range(len(scores[0])),dtype=int),
                max_boxes_to_draw= 500)

            #write out image
            cv2.imwrite(IMAGE_NAME,image)
        return  countCells,fileNameList


    def runTreatmentAnalysis(self,subfolder,xlsFileName):
        countCells,fileNameList = self.analyseImageList(subfolder,xlsFileName)
        sumList1 = countCells[:,0].tolist()
        sumList2 = countCells[:,1].tolist()
        sumList1.append(" ")
        sumList2.append(" ")
        sumList1.append(countCells[:,0].sum())
        sumList2.append(countCells[:,1].sum())
        fileNameList.append(" ")
        fileNameList.append("total ")
        data_OUT = [fileNameList,sumList1,sumList2]
        data_OUT = list(map(list, zip(*data_OUT)))
        df = pd.DataFrame(data_OUT, columns = ['fileName','alive', 'dead']) 
        df.to_excel(self.writer, sheet_name='Summary')
        self.writer.save()
        return np.array([countCells[:,0].sum(),countCells[:,1].sum()])

    def runExperimentAnalysis(self,zipPos):
        # Extract zip file
        self.EXP_DIR =self.unzip(zipPos)
        
        # Convert all images to PNG and remove TIFS
        self.convertTIF2PNG()
        
        # Get all treatment directories 
        self.TREATMENT_DIRS = [d[0] for d in os.walk(self.EXP_DIR)]
        self.TREATMENT_DIRS = self.TREATMENT_DIRS[1::] # to get rid of parent directory


        # Load the Tensorflow model into memory.
        self.setUp_tensorFlow()
        
        #variables for summary over treatments
        treatmentSummary = np.zeros([len(self.TREATMENT_DIRS),self.NUM_CLASSES],dtype=int)
        treatmentNames   = list()
        treatI =0
        
        for treatment in self.TREATMENT_DIRS:
            self.imgList = self.getImagePos_search(treatment,'.png')
            (outPath,xlsFileName) = os.path.split(treatment)
            treatmentSummary[treatI,:] = self.runTreatmentAnalysis(self.EXP_DIR,xlsFileName+'.xlsx')
            treatmentNames.append(xlsFileName)
            treatI+=1
            
        # prepare data for pandas
        sumList1 = treatmentSummary[:,0].tolist()
        sumList2 = treatmentSummary[:,1].tolist()
        data_OUT = [treatmentNames,sumList1,sumList2]
        data_OUT = list(map(list, zip(*data_OUT)))
        df = pd.DataFrame(data_OUT, columns = ['treatment','alive', 'dead']) 
        
        #writeOut to XLSX
        self.setUp_XLSwriter(self.EXP_DIR,'summary.xlsx')
        df.to_excel(self.writer, sheet_name='Summary')
        self.writer.save()

        #zip results
        self.zipResults()
        #clean up
        self.deleteWorkDir()
        print(zipPos)
        self.deleteOriginalZip(zipPos)
        print('Done')


    def deleteWorkDir(self):
        for root, dirs, files in os.walk(self.EXP_DIR, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.EXP_DIR)
    
    def deleteOriginalZip(self,zipPos):
        os.remove(zipPos)


    def zipResults(self):
        (outPath,fileName) = os.path.split(self.EXP_DIR)
        prefixLen = len(self.EXP_DIR)
        zipf = ZipFile(os.path.join(self.OUTPUT_DIR,fileName+'_ana.zip'), 'w', ZIP_DEFLATED)
        
        # ziph is zipfile handle
        for root, dirs, files in os.walk(self.EXP_DIR):
            for file in files:
                fPos = os.path.join(root, file)
                zPos = fPos[prefixLen::]
                zipf.write(fPos,zPos)
        zipf.close()

    def unzip(self,zipPos):

        # safely make new directory
        (outPath,fileName) = os.path.split(zipPos)
        newDirName = fileName[0:-4]
        newDirName = os.path.join(self.WORK_DIR,newDirName)
        if not os.path.exists(newDirName):
            os.mkdir(newDirName)
        
        # Create a ZipFile Object and load sample.zip in it
        with ZipFile(zipPos, 'r') as zipObj:
            # Extract all the contents of zip file in different directory
            zipObj.extractall(newDirName)
        return newDirName

    def convertTIF2PNG(self):
        tifList = self.getImagePos_search(self.EXP_DIR,'.tif')
        for tif in tqdm(tifList,desc='tif->png'):
            png = tif[0:-3]+'png'
            im = Image.open(tif)
            im.save(png)
            os.remove(tif)