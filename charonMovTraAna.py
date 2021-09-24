import pandas as pd
import numpy as np
from tqdm import tqdm

import cv2,os,charonMovTraReader,charonPresenter
import matplotlib.pyplot as plt
from importlib import reload
class charonMovTraAna():
    """This class analyses the tra files produced by charon movie classification.

       It will seperate them into different trajectories based on their names, translate
       the coordinate system from image coordinates into real world coordinates, determine
       a trajectory based yaw, and interpolate missing detections. 
    """

    def __init__(self,traFile,movFile=None, movParams=None):
        """This function initialises the class, awaiting the fileposition of the trajectory
            file and optionally the file position of the original movie.

        Args:
            traFile (string): absolute position of the trajectory file
            movFile (string, optional): Absolute position of the trajectory file. Defaults to None.
            movParams (list, optional): A list holding the fps,width,height and total number of 
                                        frames in the movie. Defaults to None.
        """        
        self.traFilePos = traFile
        self.movFilePos = movFile
        if self.movFilePos == None and movParams == None:
            raise ValueError('Either the movie position must be defined or the movie parameters!')
        else:

            if os.path.isfile(self.movFilePos):
                video = cv2.VideoCapture(self.movFilePos)
                self.fps          =     video.get(cv2.CAP_PROP_FPS)
                self.frame_width  = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
                self.frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
                self.frame_count  = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
                self.duration_s   = self.frame_count/self.fps
                video.release()
            else:
                self.fps          = movParams[0]
                self.frame_width  = movParams[1]
                self.frame_height = movParams[2]
                self.frame_count  = movParams[3]
                self.duration_s   = self.frame_count/self.fps
        
        traReader = charonMovTraReader.charonMovTraReader(traFile,[self.fps,self.frame_width,self.frame_height,self.frame_count])
        self.df = traReader.main()
        self.cPresenter = None
        del(traReader)

    def calculateCenter(self):
        """This function calculates the middle of the bounding box.
        """                      
        self.df['x_mean'] = (self.df['x_min'] + self.df['x_max'])/2.0
        self.df['y_mean'] = (self.df['y_min'] + self.df['y_max'])/2.0

    def writeOutDetectionDataFrame(self,fPos):
        self.df.to_hdf(fPos,key='df')

    def writeOutAnalysedFrame(self,fPos,imageScale,frame,showFrames=False):
        self.initCharonPresenter(frame,imageScale)
        self.cPresenter.showFlag = showFrames
        frame = self.cPresenter.main(10,False)
        cv2.imwrite(fPos, frame)
    
    def writeOutAnaMovie(self,fPos,imageScale,frames=None,showFrames=False):
        self.initCharonPresenter(0,imageScale)
        self.cPresenter.showFlag = showFrames
        if frames == None:
            frames = (0,self.frame_count)

        startWriter= True
        for frameI in tqdm(range(frames[0],frames[1]),desc='write movie'):
            self.cPresenter.frameNo = frameI
            frame = self.cPresenter.main(10,False)

            if startWriter:
                # important the frame shape of numpy and cv2 is often transposed!
                out = cv2.VideoWriter(fPos,cv2.VideoWriter_fourcc(*'mp4v'), movAna.fps, (frame.shape[1],frame.shape[0]))
                startWriter = False
            out.write(frame)
     
        out.release()
    
    def initCharonPresenter(self,frame,imageScale):
        if self.cPresenter == None:
            self.cPresenter = charonPresenter.charonPresenter(movF,detF,mode='video',frameNo =frame,imageScale=imageScale)
            #write detections to presenter object
            self.cPresenter.df = self.df
            self.cPresenter.detFileLoaded = True

movF = '/media/gwdg-backup/BackUp/penguins/Gentoo/Gentoo_02-03-2021_Dato1.mp4'
pathOut = '/media/gwdg-backup/BackUp/penguins/Gentoo/Gentoo_02-03-2021_Dato1_Ana.mp4'
traF = '/media/gwdg-backup/BackUp/penguins/Gentoo/Gentoo_02-03-2021_Dato1.tra'
detF = '/media/gwdg-backup/BackUp/penguins/Gentoo/Gentoo_02-03-2021_Dato1.h5'
detF = './test.h5'
imgOut = './test.png'
movOut = '/media/dataSSD/transcodeFiles/test.mp4'

movAna = charonMovTraAna(traF,movF)
movAna.calculateCenter()

#movAna.writeOutAnalysedFrame(imgOut,1.0,27989)
movAna.writeOutAnaMovie(movOut,0.5)