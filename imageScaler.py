import os, generate_tfrecord,xml_to_csv,shutil,re,cv2
from tqdm import tqdm
import xml.etree.ElementTree as ET
from PIL import Image
from pathlib import Path
import numpy as np

class imageScaler:
    def __init__(self,IMG_DIR,maxEdge,sourceImgType ='png',overWriteMode=False):
    
        self.IMG_DIR       = IMG_DIR # where the original image data is
        self.maxEdge       = int(maxEdge) # h = horizontal | v = vertical | b = both vertical and horizontal
        self.sourceImgType = sourceImgType # image type png,tif,jpg
        self.overWriteMode = overWriteMode
        self.rescaleFactor  = 1.0
        self.imagePos      = list()
        self.xmlPos        = list()
    
            
    def getFilePos_search(self):
        
        self.imagePos = list()
        # r=root, d=directories, f = files
        for r, d, f in os.walk(self.IMG_DIR):
            for file in f:
                if self.sourceImgType in file:
                    self.imagePos.append(os.path.join(r, file))
        self.imagePos.sort()
    
    def getXMLpos(self):
        self.xmlPos = [ x[:-3]+'xml' for x in self.imagePos]

    def cleanLists(self):
        # test if file exists
        boolList       = [os.path.isfile(x) for x in self.xmlPos]
        # generate only if value is true
        self.xmlPos   = [i for (i, v) in zip(self.xmlPos  , boolList) if v]
        self.imagePos = [i for (i, v) in zip(self.imagePos, boolList) if v]

    def readImg(self,imgPos):
        return cv2.imread(imgPos)
    
    def writeImg(self,img,imgPos):
        cv2.imwrite(imgPos,img)

    def scaler(self,img):
        (h, w) = img.shape[:2]

        if h <= self.maxEdge and w <= self.maxEdge:
            resizeType = 'None'
        elif h > self.maxEdge and w < self.maxEdge:
            resizeType = 'height'
        elif h < self.maxEdge and w > self.maxEdge:  
            resizeType = 'width'
        else: # both are larger than max edge
            if h>w: #image is higher than wide
                resizeType = 'height'
            else:
                resizeType = 'width'

        if resizeType == 'height':
            self.rescaleFactor  = self.maxEdge/h
            self.newDim = (int(w*self.rescaleFactor),self.maxEdge)
            return cv2.resize(img,self.newDim, interpolation = cv2.INTER_AREA)
        elif resizeType == 'width':
            self.rescaleFactor  = self.maxEdge/w
            self.newDim =  (self.maxEdge,int(h*self.rescaleFactor))
            return cv2.resize(img,self.newDim, interpolation = cv2.INTER_AREA)
        else:
            self.rescaleFactor  = 1.0
            self.newDim = (w,h)
            return img

    def scaleImage(self,imgPos):
        img = self.readImg(imgPos)
        imgResized = self.scaler(img)
        self.writeImg(imgResized,self.updateFileName(imgPos))


    def updateFileName(self,fileName):     
        if self.overWriteMode:
            return fileName
        else:   
            return fileName[:-4]+'_rs'+fileName[-4:]




    def readXMLroot(self,xmlPos):
        #read in file
        tree = ET.parse(xmlPos)
        # get start of file
        return tree,tree.getroot() 

    def setImageSizeFromXML(self,xmlRoot):
        #get image size
        size = xmlRoot.find('size')
        img_width = size.find('width')
        img_height = size.find('height')
        img_width.text  = str(self.newDim[0])
        img_height.text = str(self.newDim[1])
        
    def scaleXMLCoord(self,xmlRoot):

        coords = list(xmlRoot.iter('xmax'))+list(xmlRoot.iter('xmin'))+list(xmlRoot.iter('ymax'))+list(xmlRoot.iter('ymin'))
        for coord in coords:
            oldCoord = int(coord.text)
            newCoord = int(self.rescaleFactor *oldCoord)
            coord.text = str(newCoord)
        

    def changeFilePosInXML(self,xmlRoot):        
        fileNameNode = xmlRoot.find('filename')
        fileNameStr  = fileNameNode.text
        fileNameNode.text = self.updateFileName(fileNameStr)
        
        pathNode = xmlRoot.find('path')
        pathStr  = pathNode.text
        pathNode.text = self.updateFileName(pathStr)
    
    def updateXML(self,xmlPos):
        tree,xmlRoot  = self.readXMLroot(xmlPos)
        self.setImageSizeFromXML(xmlRoot)
        self.changeFilePosInXML(xmlRoot)
        self.scaleXMLCoord(xmlRoot)
        tree.write(self.updateFileName(xmlPos))
    
    def scaleFolder(self):
        self.getFilePos_search()
        self.getXMLpos()
        self.cleanLists()
        for imgPos,xmlPos in tqdm(list(zip(self.imagePos,self.xmlPos)),desc='resize images'):
            self.scaleImage(imgPos)
            self.updateXML(xmlPos)
