from functools import cmp_to_key
import cv2 as cv
import numpy as np
from numpy.lib.function_base import append
from tqdm import tqdm
import imutils
from matplotlib import pyplot as plt

class ShapeDetector:
    def __init__(self):
        pass
    def detect(self, c):
        # initialize the shape name and approximate the contour
        shape = "unidentified"
        peri = cv.arcLength(c, True)
        approx = cv.approxPolyDP(c, 0.04 * peri, True)
        
        # if the shape is a triangle, it will have 3 vertices
        if len(approx) == 3:
            shape = "triangle"
        # if the shape has 4 vertices, it is either a square or
        # a rectangle
        elif len(approx) == 4:
            # compute the bounding box of the contour and use the
            # bounding box to compute the aspect ratio
            (x, y, w, h) = cv.boundingRect(approx)
            ar = w / float(h)
            # a square will have an aspect ratio that is approximately
            # equal to one, otherwise, the shape is a rectangle
            shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
        # if the shape is a pentagon, it will have 5 vertices
        elif len(approx) == 5:
            shape = "pentagon"
        # otherwise, we assume the shape is a circle
        else:
            shape = "circle"
        # return the name of the shape
        return shape


class frameAverager:
    def __init__(self,filePos,numOfKeyFrames):
        self.filePos = filePos
        self.numOfKeyFrames = numOfKeyFrames
        self.vidcap = cv.VideoCapture(self.filePos)
        self.totalFrames = self.vidcap.get(cv.CAP_PROP_FRAME_COUNT)
        self.frameWidth = self.vidcap.get(cv.CAP_PROP_FRAME_WIDTH)
        self.frameHeight = self.vidcap.get(cv.CAP_PROP_FRAME_HEIGHT)
        self.fps = self.vidcap.get(cv.CAP_PROP_FPS)

    def getKeyFrames(self):
        self.keyFrameIndex = np.linspace(0,self.totalFrames-1,self.numOfKeyFrames,dtype=int)
        self.keyFrameList = list()

        for keyFrame in tqdm(self.keyFrameIndex):
            self.vidcap.set(cv.CAP_PROP_POS_FRAMES,keyFrame)
            success,image = self.vidcap.read()
            if success == True:    
                self.keyFrameList.append(image)
    
    def getFrameAvg(self,imgList):
        avg_img = np.mean(imgList, axis=0)
        return avg_img.astype(np.uint8)
    
    def run(self):
        self.getKeyFrames()
        return self.getFrameAvg(self.keyFrameList)

class localContrastEnhancer:
    def __init__(self,image,filterSize,kernelSize):
        self.image = image
        self.filterSize = filterSize
        self.kernelSize = kernelSize

    def run(self):
        #remove small noise via median:
        imageMedian = cv.medianBlur(self.image, self.filterSize)

        # Get local maximum:
        maxKernel = cv.getStructuringElement(cv.MORPH_RECT, (self.kernelSize, self.kernelSize))
        localMax = cv.morphologyEx(imageMedian, cv.MORPH_CLOSE, maxKernel, None, None, 1, cv.BORDER_REFLECT101)

        # Perform gain division
        gainDivision = np.where(localMax == 0, 0, (self.image/localMax))

        # Clip the values to [0,255]
        gainDivision = np.clip((255 * gainDivision), 0, 255)

        # Convert the mat type from float to uint8:
        gainDivision = gainDivision.astype("uint8") 

        # Convert RGB to grayscale:
        return cv.cvtColor(gainDivision, cv.COLOR_BGR2GRAY)

class  contourGrabber:
    def __init__(self,image,threshold):
        self.image = image
        self.threshold = threshold
        self.sd = ShapeDetector()
    
    def resize(self):
        # resize the image to a smaller factor so that the shapes can be approximated better
        self.img_resized = imutils.resize(self.image, width=300)
        self.ratio = self.image.shape[0] / float(self.img_resized.shape[0])

    def blur(self,image):
        return cv.GaussianBlur(image, (5, 5), 0)
    
    def binarise(self,image):
        return cv.threshold(image, 220, 255, cv.THRESH_BINARY)[1]
    
    def grab_contours(self,img_binarised):
        # find contours in the thresholded image and initialize the shape detector
        cnts = cv.findContours(img_binarised.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        return imutils.grab_contours(cnts)
                
    def run(self):
        self.resize()
        self.img_blurred   = self.blur(self.img_resized)
        self.img_binarised = self.binarise(self.img_blurred)
        self.contours      = self.grab_contours(self.img_binarised)
        self.collateResulsts(self.contours)
        return self.result

    def collateResulsts(self,contourList):
        self.result = list()
        # loop over the contours
        for contour in contourList:
            # compute the center of the contour, then detect the name of the
            # shape using only the contour
            M = cv.moments(contour)
            cX = int((M["m10"] / M["m00"]) * self.ratio)
            cY = int((M["m01"] / M["m00"]) * self.ratio)
            shape = self.sd.detect(contour)
            # multiply the contour (x, y)-coordinates by the resize ratio,
            # then draw the contours and the name of the shape on the image
            contour = contour.astype("float")
            contour = np.squeeze(contour)
            contour *= self.ratio
            contour = contour.astype("int")
            # get the arclength of the countour
            arcLen = cv.arcLength(contour, True)
            # get the bounding box
            boundingBox = (contour[:,0].min(),contour[:,1].min(),contour[:,0].max(),contour[:,1].max())

            self.result.append((cX,cY,arcLen,boundingBox,shape,contour))
        return self.result

    def showContours(self,image):
        for res in self.result:
            cX,cY,aL,bb,shape,c = res[:]
            cv.drawContours(image, [c], -1, (0, 255, 0), 2)
            cv.putText(image, shape, (cX, cY), cv.FONT_HERSHEY_SIMPLEX,0.5, (255, 255, 255), 2)
            image = cv.rectangle(image, bb[0:2], bb[2::], (255,0,0), 2)
        # show the output image
        cv.imshow("Image", image)


class arenaFinder:
    def __init__(self,videoFilePos,numOfKeyFrames = 50,filterSize=5,kernelSize=100,threshold=220):
        self.videoFilePos = videoFilePos
        self.numOfKeyFrames = numOfKeyFrames
        self.filterSize = filterSize
        self.kernelSize = kernelSize
        self.threshold = threshold

    def getFalseArenas(self,arcLen):
        avg_arcLen = np.mean(arcLen)
        std_arcLen = np.std(arcLen)
        lowerLim = avg_arcLen-std_arcLen
        upperLim = avg_arcLen+std_arcLen
        toosmall =  np.argwhere(arcLen < lowerLim)
        toolarge =  np.argwhere(arcLen > upperLim)
        return np.squeeze(np.vstack((toosmall,toolarge)))

    def cleanResults(self):
        arcLength   = np.array([x[2] for x in self.rawResults]) 
        falsePosInd = self.getFalseArenas(arcLength)
        self.results = self.rawResults.copy()
        del self.results[falsePosInd]

    def makeCalcShortHands(self):
        arcLength   = np.array([x[2] for x in self.results]) 
        bbList      = np.vstack([np.array(x[3]) for x in self.results])
        centerList  = np.vstack([np.hstack(np.array(x[0:2])) for x in self.results])
        return centerList,bbList,arcLength


    def run(self):     
        # get average frame of video
        self.fA = frameAverager(self.videoFilePos,self.numOfKeyFrames)
        self.avgImg = self.fA.run()
        # enhance the local contrast in average frame
        lCE = localContrastEnhancer(self.avgImg,self.filterSize,self.kernelSize)
        self.avgImgEnh = lCE.run()
        cG = contourGrabber(self.avgImgEnh,self.threshold)
        self.rawResults = cG.run()
        self.cleanResults()
        self.centerList,self.bbList, self.arcLenList = self.makeCalcShortHands()
        self.calculateMeanBoundingBoxes()
        self.drawFoundArenas()
        return self.avg_boundingBox
    
    def calculateMeanArena(self):
        self.avg_arena_width = int(np.round(np.mean(self.bbList[:,2]-self.bbList[:,0])))
        if self.avg_arena_width%2 ==1: self.avg_arena_width+=1
        self.avg_arena_height = int(np.round(np.mean(self.bbList[:,3]-self.bbList[:,1]))) 
        if self.avg_arena_height%2 ==1: self.avg_arena_height+=1

    def calculateMeanCenters(self):

        self.centerList = self.centerList[self.centerList[:, 0].argsort()]  # sort by day
        xPattern = np.zeros(shape=(6,)) 
        for i in range(6):
            xPattern[i] = int(np.round(np.mean(self.centerList[i*9:(i+1)*9,0])))

        self.centerList = self.centerList[self.centerList[:, 1].argsort()]  # sort by day
        yPattern = np.zeros(shape=(9,)) 
        for i in range(9):
            yPattern[i] = int(np.round(np.mean(self.centerList[i*6:(i+1)*6,1])))

        avg_centers=list()
        for x in xPattern:
            for y in yPattern:
                avg_centers.append([x,y])    
        self.avg_centers = np.array(avg_centers,dtype=int)
        self.avg_centers = self.avg_centers[self.avg_centers[:, 1 ].argsort(kind='mergesort')]
        self.avg_centers = np.array(np.column_stack((self.avg_centers,np.linspace(1,54,54))),dtype=int)

    def calculateMeanBoundingBoxes(self,offsetX=15,offsetY=15, mode='contourCenter'):
        self.calculateMeanArena()
        self.calculateMeanCenters()
        avg_bb = list()
        for i in range(54):
            if mode=='average':
                avg_bb.append([self.avg_centers[i,0]-(self.avg_arena_width/2+offsetX),self.avg_centers[i,1]-(self.avg_arena_height/2++offsetY),
                           self.avg_centers[i,0]+(self.avg_arena_width/2+offsetX),self.avg_centers[i,1]+(self.avg_arena_height/2++offsetY),self.avg_centers[i,2]])
            elif mode == 'contourCenter':
                avg_bb.append([self.centerList[i,0]-(self.avg_arena_width/2+offsetX),self.centerList[i,1]-(self.avg_arena_height/2++offsetY),
                           self.centerList[i,0]+(self.avg_arena_width/2+offsetX),self.centerList[i,1]+(self.avg_arena_height/2++offsetY),i])

            else:
                raise ValueError(f'arenaFinder:calculateMeanBoundingBoxes: mode has unknown value {mode}')
        self.avg_boundingBox = np.array(avg_bb,dtype=int)
        self.avg_boundingBox[self.avg_boundingBox < 0] = 0
        self.avg_boundingBox[self.avg_boundingBox[:,3]>self.fA.frameHeight,3] = self.fA.frameHeight
        self.avg_boundingBox[self.avg_boundingBox[:,2]>self.fA.frameWidth,2]  = self.fA.frameWidth

    def drawFoundArenas(self):
        image = self.avgImg.copy()
        for i in range(54):
            cv.putText(image, str(self.avg_centers[i,2]), (self.avg_centers[i,0], self.avg_centers[i,1]), cv.FONT_HERSHEY_SIMPLEX,0.5, (255, 255, 255), 2)
            image = cv.rectangle(image, tuple(self.avg_boundingBox[i,0:2]), tuple(self.avg_boundingBox[i,2:4]), (255,0,0), 2)
        cv.imshow('These are the 54 split movies',image)
    
