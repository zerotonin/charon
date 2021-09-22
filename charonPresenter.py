
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

    def getDetections(self):
        pass

    def presentImage(self):
        pass
    
    def saveImage(self):
        pass