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
        self.setLarvalParameters()

    def setLarvalParameters(self):
        self.medianFilterKernel = 3

        self.cannyPara1         = 80
        self.cannyPara2         = 9
        
        self.houghMinR          = 8
        self.houghMaxR          = 12
        self.houghMinDist       = 8

    def setPrePupaParameters(self):
        self.medianFilterKernel = 3

        self.cannyPara1         = 80
        self.cannyPara2         = 9
        
        self.houghMinR          = 4
        self.houghMaxR          = 10
        self.houghMinDist       = 5

    def readImage(self,fileName):
        self.img = cv2.imread(fileName)

    def img2gray(self,image):
        return cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    
    def filterImg(self,image,kernel):
        return cv2.medianBlur(image,kernel)

    def imageMorph(self):
        self.img_gray   = self.img2gray(self.img)
        self.img_blurred = self.filterImg(self.img_gray,self.medianFilterKernel)
    
    def getHoughCircles(self):
        # docstring of HoughCircles: HoughCircles(image, method, dp, minDist[, circles[, param1[, param2[, minRadius[, maxRadius]]]]]) -> circles
        return cv2.HoughCircles(self.img_blurred, cv2.HOUGH_GRADIENT, 1, self.houghMinDist, 
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
    
    def makeDataFrame(self,fileName,circles):
        # calc bounding boxes
        bboxes  = self.circles2boundingBoxes(circles)
        # make dataframe
        if len(circles.shape)<2:
            cellDF = pd.DataFrame(dict(zip(['x_min','y_min','x_max','y_max','x_cen','y_cen','radius'],list(np.hstack((bboxes,circles))))),index=[0])
        else:
            cellDF = pd.DataFrame(np.hstack((bboxes,circles)),columns=['x_min','y_min','x_max','y_max','x_cen','y_cen','radius'])
        # add file position
        cellDF['fileName'] = fileName
        return cellDF

    def makeXML(self,fileName,circles, imgShape):
        # calc bounding boxes
        bboxes  = self.circles2boundingBoxes(circles)
        # make xml
        xmlPos =fileName[:-3]+'xml'
        xmlFileNameField = os.path.basename(fileName)
        xmlFolderField = os.path.basename(os.path.dirname(fileName))
        xmlObjectTag = 'cell'
        file1 = open(xmlPos,"w")
        file1.write(f'<annotation>\n')
        file1.write(f'	<folder>{xmlFolderField}</folder>\n')
        file1.write(f'	<filename>{xmlFileNameField}</filename>\n')
        file1.write(f'	<path>{fileName}</path>\n')
        file1.write(f'	<source>\n')
        file1.write(f'		<database>Unknown</database>\n')
        file1.write(f'	</source>\n')
        file1.write(f'	<size>\n')
        file1.write(f'		<width>{int(imgShape[1])}</width>\n')
        file1.write(f'		<height>{int(imgShape[0])}</height>\n')
        file1.write(f'		<depth>{int(imgShape[2])}</depth>\n')
        file1.write(f'	</size>\n')
        file1.write(f'	<segmented>0</segmented>\n')
        if len(circles.shape)<2:
            file1.write(f'	<object>\n')
            file1.write(f'		<name>{xmlObjectTag}</name>\n')
            file1.write(f'		<pose>Unspecified</pose>\n')
            file1.write(f'		<truncated>0</truncated>\n')
            file1.write(f'		<difficult>0</difficult>\n')
            file1.write(f'		<bndbox>\n')
            file1.write(f'			<xmin>{int(bboxes[0])}</xmin>\n')
            file1.write(f'			<ymin>{int(bboxes[1])}</ymin>\n')
            file1.write(f'			<xmax>{int(bboxes[2])}</xmax>\n')
            file1.write(f'			<ymax>{int(bboxes[3])}</ymax>\n')
            file1.write(f'		</bndbox>\n')
            file1.write(f'	</object>\n')
        else:
            for i in range(bboxes.shape[0]):
                file1.write(f'	<object>\n')
                file1.write(f'		<name>{xmlObjectTag}</name>\n')
                file1.write(f'		<pose>Unspecified</pose>\n')
                file1.write(f'		<truncated>0</truncated>\n')
                file1.write(f'		<difficult>0</difficult>\n')
                file1.write(f'		<bndbox>\n')
                file1.write(f'			<xmin>{int(bboxes[i,0])}</xmin>\n')
                file1.write(f'			<ymin>{int(bboxes[i,1])}</ymin>\n')
                file1.write(f'			<xmax>{int(bboxes[i,2])}</xmax>\n')
                file1.write(f'			<ymax>{int(bboxes[i,3])}</ymax>\n')
                file1.write(f'		</bndbox>\n')
                file1.write(f'	</object>\n')

        file1.write(f'</annotation>')


    def detectCellsInFile(self,fileName,plotFlag = False):

        self.readImage(fileName)
        self.imageMorph()
        circles = self.detectCircles()
        # plot
        if plotFlag:
            self.plotFrame(circles)
        # make dataframe that also includes calculating the bounding boxes
        if circles is not None:
            # get 2D list
            circles = circles.squeeze()
            cellDF  = self.makeDataFrame(fileName,circles)
            self.makeXML(fileName,circles,self.img.shape)
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
        cv2.imshow('img_blurred', self.img_blurred)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    def saveFolderDF(self,filePos):
        self.FolderDF.to_csv(filePos, index=False)
