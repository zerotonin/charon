import os,cv2
import numpy  as np
import pandas as pd
from tqdm import tqdm
from PIL import Image, ImageSequence

class drosoImgSplitter():

    def __init__(self, directory,extension='tif'):
        self.directory = directory
        self.extension = extension

    def splitImage(self,imgFile):
        im = Image.open(imgFile)
        os.makedirs(imgFile[0:-4],exist_ok=True)

        for i, page in enumerate(ImageSequence.Iterator(im)):
            saveFileName = os.path.join(imgFile[0:-4],f'page_{str(i).zfill(4)}.png')
            page.save(saveFileName)

    def splitImageDir(self):
        imgFiles = [os.path.join(self.directory,f) for f in os.listdir(self.directory) if f.endswith(self.extension)]
        for imgFile in tqdm(imgFiles,desc='splitting images'):
            self.splitImage(imgFile)



class circleDetector():
    # https://stackoverflow.com/questions/60637120/detect-circles-in-opencv
    def __init__(self):
        self.medianFilterKernel = 3

        self.cannyPara1         = 80
        self.cannyPara2         = 9
        
        self.houghMinR          = 8
        self.houghMaxR          = 12
        self.houghMinDist       = 8

    def readImage(self,fileName):
        self.img = cv2.imread(fileName)

    def img2gray(self,image):
        return cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    
    def filterImg(self,image,kernel):
        return cv2.medianBlur(image,kernel)

    def imageMorph(self):
        self.img_gray   = self.img2gray(self.img)
        self.img_blured = self.filterImg(self.img_gray,self.medianFilterKernel)
    
    def getHoughCircles(self):
        # docstring of HoughCircles: HoughCircles(image, method, dp, minDist[, circles[, param1[, param2[, minRadius[, maxRadius]]]]]) -> circles
        return cv2.HoughCircles(self.img_blured, cv2.HOUGH_GRADIENT, 1, self.houghMinDist, 
                                param1=self.cannyPara1, param2=self.cannyPara2, minRadius=self.houghMinR, 
                                maxRadius=self.houghMaxR )
    
    def detectCircles(self):
        circles = self.getHoughCircles()
        return circles
    
    def circles2boundingBoxes(self,circles):
        if len(circles.shape)<2:
            return np.array([circles[0]-circles[2],circles[1]-circles[2],circles[0]+circles[2],circles[1]+circles[2]])
        else: 
            return np.array([circles[:,0]-circles[:,2],circles[:,1]-circles[:,2],circles[:,0]+circles[:,2],circles[:,1]+circles[:,2] ]).T
    
    def makeDataFrame(self,fileName,circles,bboxes):
        if len(circles.shape)<2:
            cellDF = pd.DataFrame(dict(zip(['x_min','y_min','x_max','y_max','x_cen','y_cen','radius'],list(np.hstack((bboxes,circles))))),index=[0])
        else:
            cellDF = pd.DataFrame(np.hstack((bboxes,circles)),columns=['x_min','y_min','x_max','y_max','x_cen','y_cen','radius'])
        cellDF['fileName'] = fileName
        return cellDF


    def detectCellsInFile(self,fileName,plotFlag = False):

        self.readImage(fileName)
        self.imageMorph()
        circles = self.detectCircles()
        if plotFlag:
            self.plotFrame(circles)
        if circles is not None:
            circles = circles.squeeze()
            bboxes  = self.circles2boundingBoxes(circles)
            cellDF  = self.makeDataFrame(fileName,circles,bboxes)
            return cellDF
        else:
            return None

    def detectCellsInFolder(self,directory,extension,plotFlag = False):
        imgFiles = [os.path.join(directory,f) for f in os.listdir(directory) if f.endswith(extension)]
        dataFrameList = list()
        for imgFile in tqdm(imgFiles,desc='detectingCells'):
            dataFrameList.append(self.detectCellsInFile(imgFile,plotFlag))
        self.FolderDF = pd.concat(dataFrameList)

    def plotFrame(self,circles):
        img_result = self.img.copy()
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0,:]:
                cv2.circle(img_result, (i[0], i[1]), i[2], (0, 255, 0), 2)

        # Show result for testing:
        cv2.imshow('img', img_result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    def saveFolderDF(self,filePos):
        self.FolderDF.to_csv(filePos, index=False)