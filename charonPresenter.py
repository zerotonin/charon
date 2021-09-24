
import cv2,os,math
from bounding_box import bounding_box as bb
import pandas as pd
import numpy as np
class charonPresenter():

    def __init__(self,mediaFile,detFilePD,mode,frameNo=0,imageScale=1.0):
        self.mediaFile        = mediaFile
        self.detFilePD        = detFilePD
        self.mode             = mode
        self.frameNo          = frameNo
        self.imageScaling     = imageScale
        self.videoReaderOpen  = False
        self.detFileLoaded    = False
        self.frameOverlayFlag = True
        self.showFlag         = True
        self.videoCap         = None
        self.df               = None
        self.image            = None
        self.frame_count      = None
    
    def main(self,waitKeyDurMS=0,destroyFlag = True):
        self.detections = self.getDetections()
        self.image      = self.getImage()
        self.annotateImage()
        if self.showFlag == True:
            self.presentImage(waitKeyDurMS=waitKeyDurMS,destroyFlag=destroyFlag)
        return self.image

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
            image = self.readVideoFrame()
        elif self.mode == 'image':
            self.frameOverlayFlag = False
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
        
    def readVideoFrame(self):
        self.videoCap.set(1,self.frameNo)
        ret,frame = self.videoCap.read()
        if not ret:
            raise Exception(f'Frame {self.frameNo} could not be loaded!')
        return frame

    def annotateImage(self):
        detNum = 0
        for det in self.detections.iterrows():
            x_min = int(det[1]['x_min'] * self.image.shape[1])
            y_min = int(det[1]['y_min'] * self.image.shape[0])
            x_max = int(det[1]['x_max'] * self.image.shape[1])
            y_max = int(det[1]['y_max'] * self.image.shape[0])
            label = f"{detNum}: {det[1]['label']} {np.around(det[1]['quality'],decimals=2)}"
            bb.add(self.image,x_min,y_min,x_max,y_max,label )
            detNum += 1
        if self.frameOverlayFlag:
            self.addFrameOverlay()
        

    def presentImage(self,waitKeyDurMS = 0,destroyFlag =True):
       # cv2.imshow(f'{os.path.basename(self.mediaFile)} @ frame {self.frameNo}' , self.image)
        cv2.imshow(f'{os.path.basename(self.mediaFile)}' , self.image)
        cv2.waitKey(waitKeyDurMS) & 0XFF
        if destroyFlag:
            cv2.destroyAllWindows()
        
    
    def getDigits(self,n):
        if n > 0:
                digits = int(math.log10(n))+1
        elif n == 0:
            digits = 1
        else:
            digits = int(math.log10(-n))+2 # +1 if you don't count the '-' 
        return digits
    
    def addFrameOverlay(self):
        digitLength = self.getDigits(self.frame_count)
        frameStr = format(self.frameNo,f'{digitLength}d')
        totalStr  = str(self.frame_count)
        overlayStr = f'frame {frameStr} of {totalStr}'
        cv2.putText(
            self.image, #numpy array on which text is written
            overlayStr, #text
            (10,30), #position at which writing has to start
            cv2.FONT_HERSHEY_PLAIN, #font family
            1, #font size
            (209, 80, 0, 128), #font color
            1)
        pass