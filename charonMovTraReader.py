import pandas as pd
import numpy as np
import cv2,os
from tqdm import tqdm

class charonMovTraReader():
    """This class analyses the tra files produced by charon movie classification.

       It will seperate them into different trajectories based on their names, translate
       the coordinate system from image coordinates into real world coordinates, determine
       a trajectory based yaw, and interpolate missing detections. 
    """

    def __init__(self,traFile,movParams):
        """This function initialises the class, awaiting the fileposition of the trajectory
            file and optionally the file position of the original movie.

        Args:
            traFile (string): absolute position of the trajectory file
            movParams (list): A list holding the fps,width,height and total number of 
                                        frames in the movie.
        """        
        self.traFilePos = traFile
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
        for line in tqdm(Lines,desc='reading tra file'):
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

    def buildDataFrame(self):
        """This function builds the dataframe from the list data.
           
           [pandas dataframe]: a pandas data frame with hierarchical indexing the first index is time in
                            seconds the second the number of detection. If multiple detections are in
                            the frame they get number from 0 to n. The columns are the label of the 
                            detection followed by the bounding box as x_min, y_min,x_max, and y_max in
                            normalised pixel coordinates
        """        
        # get the maximal number of detections
        self.maxDetections = np.array([len(x[1]) for x in self.dataList]).max()
        # these are the fix column labels from  charon
        columns    = ['label','quality','x_min','y_min','x_max','y_max']
        # index 
        self.df = pd.DataFrame(self.makeTallFormatList(), index=self.makeMultiIndeces(),columns = columns)
        # time  stamps 
        timeStamps = np.linspace(0,self.duration_s,self.frame_count)
        timeStamps = [np.full((1,self.maxDetections),x).tolist() for x in timeStamps]
        timeStamps = self.flattenList(self.flattenList(timeStamps))
        self.df['time_s'] = timeStamps
 
    def makeMultiIndeces(self):
        """This function creates to arrays with the time and detection indices.

        Returns:
            list of arrays: the first entry is a numpy array with all timestamps. Each time
                            stamp is repeated self.maxDetections times. The second entry
                            is a list of all detections repeated self.frame_count times.
        """    
        # frame index
        frameIndex = np.linspace(0,self.frame_count-1,self.frame_count,dtype=int)
        frameIndex = [np.full((1,self.maxDetections),x).tolist() for x in frameIndex]
        frameIndex = self.flattenList(self.flattenList(frameIndex))
    

        detIndex = [ list(range(self.maxDetections)) for x in range(self.frame_count)]
        detIndex = self.flattenList(detIndex)
        
        return [frameIndex,detIndex]

    def flattenList(self,bulkList):
        """This function flattens a list of list, into a one dimensional list

        Args:
            bulkList (list): a list containing a list

        Returns:
            [list]: a list containing one nesting level less
        """        
        # flatten list
        return [item for sublist in bulkList for item in sublist]

    def makeTallFormatList(self):
        """[summary]

        Returns:
            [list]: a list with every detection possible in there. If in some frames
                    there were less detetections than self.maxDetections. Those will
                    be filled with an empty row ['',-1,0,0,0,0]. These will be deleted
                    in the self.main() function
        """        
        dataListTall = list()
        for frame in tqdm(self.dataList,desc='tall list format'):
            det_count = len(frame[1])
            for det in frame[1]:
                dataListTall.append(list(det))
            for emptyDet in range(self.maxDetections-det_count):
                det= list()
                det.append('')
                det.append(-1)
                for i in range(4):
                    det.append(0)
                dataListTall.append(det)
        return dataListTall
    
    def main(self):
        """ This creates a dataframe from a tra file.

        Attention
        ---------
        The tra file has a line for every frame. The resulting data frame ommits 'empty' frames. Therefor
        there is no fixed time code in this representation. The user has to check if the data is jumping
        over non detected frames.

        Returns:
            [pandas dataframe]: a pandas data frame with hierarchical indexing the first index is time in
                                seconds the second the number of detection. If multiple detections are in
                                the frame they get number from 0 to n. The columns are the label of the 
                                detection followed by the bounding box as x_min, y_min,x_max, and y_max in
                                normalised pixel coordinates
        """        
        self.readTRAfile()
        self.buildDataFrame()
        #get rid of the empty lines
        self.df =self.df[self.df['quality'] > -1]
        return self.df
