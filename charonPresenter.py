
import cv2
from bounding_box import bounding_box as bb
import os
import pandas as pd

class charonPresenter():

    def __init__(self,mediaFile,detFilePD,mode,frameNo=0):
        self.mediaFile       = mediaFile
        self.detFilePD       = detFilePD
        self.mode            = mode
        self.frameNo         = frameNo
        self.videoReaderOpen = False
        self.detFileLoaded   = False
        self.saveFlag        = False
        self.saveFormat      = None # 'image' or 'video'          
        self.savePos         = None
        self.videoCap        = None
        self.df              = None
        self.image           = None
        self.frame_count     = None
        self.imageScaling    = 1.0
    
    def main(self):
        self.detections = self.getDetections()
        self.image      = self.getImage()
        self.annotateImage()
        self.presentImage()
        if self.saveFlag:
            self.saveImage()

    def getDetections(self):
        if not self.detFileLoaded:
            self.df  = pd.read_hdf(self.detFilePD)
            self.detFileLoaded = True
        det = self.df.loc[[self.frameNo]]
        
        return det

    def getImage(self):
        if self.mode == 'video':
            if not self.videoReaderOpen:
                self.openVideoReader()
            image = self.readVideoFrame(self.frameNo)
        elif self.mode == 'image':
            image = cv2.imread(self.mediaFile, cv2.IMREAD_COLOR)
        else:
            raise ValueError(f'charonPresenter:main:media modus {self.mode} not implemented.')
        
        resized = self.resizeImage(image)
        return resized

    def resizeImage(self,image):

        width  = int(image.shape[1]*self.imageScaling)
        height = int(image.shape[0]*self.imageScaling)
        return cv2.resize(image, (width,height), interpolation = cv2.INTER_AREA)

        
    def openVideoReader(self):
        self.videoCap = cv2.VideoCapture(self.mediaFile)
        self.frame_count  = int(self.videoCap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.videoReaderOpen = True
        
    def readVideoFrame(self,frameNo):
        self.videoCap.set(1,self.frameNo/self.frame_count)
        ret,frame = self.videoCap.read()
        if not ret:
            raise Exception(f'Frame {self.frameNo} could not be loaded!')
        return frame

    def annotateImage(self):
        for det in self.detections.iterrows():
            x_min = int(det[1]['x_min'] * self.image.shape[1])
            y_min = int(det[1]['y_min'] * self.image.shape[0])
            x_max = int(det[1]['x_max'] * self.image.shape[1])
            y_max = int(det[1]['y_max'] * self.image.shape[0])
            label = det[1]['label']
            print('image',self.image)
            bb.add(self.image,x_min,y_min,x_max,y_max,label )
        

    def presentImage(self):
        cv2.imshow(f'{os.path.basename(self.mediaFile)} @ frame {self.frameNo}' , self.image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    
    def saveImage(self):
        pass