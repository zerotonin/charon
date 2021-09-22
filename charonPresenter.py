
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
    
    def main(self):
        detections = self.getDetections()
        image      = self.getImage()
        image = self.annotateImage(image,detections)
        self.presentImage()
        if self.saveFlag:
            self.saveImage()

    def getDetections(self):
        if not self.detFileLoaded:
            self.df  = pd.read_hdf(self.detFilePD)
        det = self.df[[self.frameNo]]
        
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
        
        return image

        
    def openVideoReader(self):
        self.videoCap = cv2.VideoCapture(self.mediaFile)
        self.videoReaderOpen = True
        
    def readVideoFrame(self,frameNo):
        self.videoCap.set(2,self.frameNo)
        ret,frame = self.videoCap.read()
        return frame

    def annotateImage(self,image,detections):
        
        for det in detections:
            bb.add(image, det['x_min'], det['y_min'], det['x_max'], det['y_max'], det['label'])
            return image
        

    def presentImage(self, image):
        cv2.imshow(f'{os.path.basename(self.mediaFile)} @ frame {self.frameNo}' , image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    
    def saveImage(self):
        pass