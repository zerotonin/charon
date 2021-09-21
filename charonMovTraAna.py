import pandas as pd
import numpy as np
import cv2,os

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


    def readTRAfile(self):
        """ This function reass the trafile and returns the data as a list of tuples.

            self.dataList = [(x,[a,b,c,d]),(x+1,[a,b]),(x+2,[a,b,c]),...(x+n,[a,b,c])]

            example: a = (qual,x1,y1,x2,y2)

            The resulting data list is a list of tuples. Each tuple holds the frame
            number (e.g. x) and a list of detections (e.g. a,b,c,d). Each detection 
            is itself a tuple again with label, quality, smaller x-position (x1), larger 
            x-position (x2), smaller y-position (y1), and larger y-position (y2).
            x1, y1, x2, and y2 make the bounding box of the detection. All of them
            are in normalised coordinates 
        """        
        traFile = open(self.traFilePos, 'r')
        Lines = traFile.readlines()
        self.dataList = list()
        for line in Lines:
            self.dataList.append(self.splitLine(line))
        traFile.close()
    
    def splitLine(self,line):
        """This function splits a line in a trajectory file into the single components


        Args:
            line (String): a line from a charon movie trajectory file

        Returns:
            tuple: a tuple like (x,[a,b,c,d]). The first entry (x) is the frame number,
                   the second entry is a list of detections. Each detection (e.g. a )
                   is itself a tuple again with label, quality, smaller x-position (x1), 
                   larger  x-position (x2), smaller y-position (y1), and larger y-position 
                   (y2). x1, y1, x2, and y2 make the bounding box of the detection. All 
                   of them are in normalised coordinates 
        """        
        frameNo,detections = line.split(':')
        listOfDetections = detections.split('<')
        listOfDetsAsTuple = list()
        for det in listOfDetections:
            if ',' in det:
                listOfDetsAsTuple.append(self.detectionToTuple(det))
        
        return (int(frameNo),listOfDetsAsTuple)

    def detectionToTuple(self,det):
        """[summary]

        Args:
            det (string): this is a substring of the original trajectory line, holding
                          just the detection part of this line

        Returns:
            tuple: Each detection is itself a tuple again with label, quality, smaller 
                   x-position (x1), larger  x-position (x2), smaller y-position (y1), 
                   and larger y-position (y2). x1, y1, x2, and y2 make the bounding box 
                   of the detection. All of them are in normalised coordinates. 
        """        
        name,qual,x1,y1,x2,y2 = det.split(',')
        return (name[2::],float(qual),float(x1),float(y1),float(x2),float(y2))




movF = '/media/gwdg-backup/BackUp/penguins/Gentoo/Gentoo_02-03-2021_Dato1.mp4'
traF = '/media/gwdg-backup/BackUp/penguins/Gentoo/Gentoo_02-03-2021_Dato1.tra'

movAna = charonMovTraAna(traF,movF)
movAna.readTRAfile()


maxDetections = np.array([len(x[1]) for x in dataList]).max()



