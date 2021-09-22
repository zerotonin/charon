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
        del(traReader)

    def calculateCenter(self):
        """This function calculates the middle of the bounding box.
        """                      
        self.df['x_mean'] = (self.df['x_min'] + self.df['x_max'])/2.0
        self.df['y_mean'] = (self.df['y_min'] + self.df['y_max'])/2.0

movF = '/media/gwdg-backup/BackUp/penguins/Gentoo/Gentoo_02-03-2021_Dato1.mp4'
traF = '/media/gwdg-backup/BackUp/penguins/Gentoo/Gentoo_02-03-2021_Dato1.tra'
detF = '/media/gwdg-backup/BackUp/penguins/Gentoo/Gentoo_02-03-2021_Dato1.h5'
detF = './test.h5'
movAna = charonMovTraAna(traF,movF)
movAna.calculateCenter()
df = movAna.df
df.to_hdf(detF,key='df')
reload(charonPresenter)
cp = charonPresenter.charonPresenter(movF,detF,mode='video',frameNo =30445)
cp.main()