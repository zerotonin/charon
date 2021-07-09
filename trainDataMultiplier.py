import os, generate_tfrecord,xml_to_csv,shutil,re,cv2
from tqdm import tqdm
import xml.etree.ElementTree as ET
from PIL import Image
from pathlib import Path
import numpy as np

class trainMultiplier:
    def __init__(self,IMG_DIR,sourceImgType ='png',flipType='hvb'):
    
        self.IMG_DIR       = IMG_DIR # where the original image data is
        self.sourceImgType = sourceImgType # image type png,tif,jpg
        self.flipType      = flipType # h = horizontal | v = vertical | b = both vertical and horizontal
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

    def readImg(self,imgPos):
        return cv2.imread(imgPos)
    
    def writeImg(self,img,imgPos):
        cv2.imwrite(imgPos,img)

    def flipIMGhoriz(self,img):
        return cv2.flip(img, 1)

    def flipIMGvert(self,img):
        return cv2.flip(img, 0)

    def flipIMGboth(self,img):
        return self.flipIMGhoriz(self.flipIMGvert(img))
    
    def updateFileName(self,fileName,flipAxStr):        
        return fileName[:-4]+flipAxStr+fileName[-4:]

    def flipImage(self,imgPos):
        img = self.readImg(imgPos)

        if 'h' in self.flipType:
            imgFlipped = self.flipIMGhoriz(img)
            writePos = self.updateFileName(imgPos,'h')
            self.writeImg(imgFlipped,writePos)
        if 'v' in self.flipType:
            imgFlipped = self.flipIMGvert(img)
            writePos = self.updateFileName(imgPos,'v')
            self.writeImg(imgFlipped,writePos)
        if 'b' in self.flipType:
            imgFlipped = self.flipIMGboth(img)
            writePos = self.updateFileName(imgPos,'b')
            self.writeImg(imgFlipped,writePos)



    def readXMLroot(self,xmlPos):
        #read in file
        tree = ET.parse(xmlPos)
        # get start of file
        return tree,tree.getroot() 

    def getImageSizeFromXML(self,xmlRoot):
        #get image size
        size = xmlRoot.find('size')
        img_width = size.find('width')
        img_height = size.find('height')
        img_size   = (int(img_width.text),int(img_height.text))
        return img_size


    def flipXMLCoord(self,xmlRoot,flipCoord,img_size):
        if flipCoord == 'x':
            sizeVal = img_size[0]
        elif flipCoord == 'y':
            sizeVal = img_size[1]
        else:
            raise ValueError('training multiplier flip coordinate is neither x nor y: ' + str(flipCoord))
        coords = list(xmlRoot.iter(flipCoord+'max'))+list(xmlRoot.iter(flipCoord+'min'))
        #update bbox values
        for coord in coords:
            oldCoord = int(coord.text)
            newCoord = sizeVal -oldCoord
            coord.text = str(newCoord)


    
    def flipXML(self,xmlPos):
        tree,xmlRoot  = self.readXMLroot(xmlPos)
        img_size = self.getImageSizeFromXML(xmlRoot) 

        if 'h' in self.flipType:
            tree,xmlRoot  = self.readXMLroot(xmlPos)
            self.flipXMLCoord(xmlRoot,'x',img_size)
            writePos = self.updateFileName(xmlPos,'h')
            tree.write(writePos)
        if 'v' in self.flipType:
            tree,xmlRoot  = self.readXMLroot(xmlPos)
            self.flipXMLCoord(xmlRoot,'y',img_size)
            writePos = self.updateFileName(xmlPos,'v')  
            tree.write(writePos)       
        if 'b' in self.flipType:
            tree,xmlRoot  = self.readXMLroot(xmlPos)
            self.flipXMLCoord(xmlRoot,'x',img_size)
            self.flipXMLCoord(xmlRoot,'y',img_size)
            writePos = self.updateFileName(xmlPos,'b')
            tree.write(writePos)
    
    def flipFolder(self):
        self.getFilePos_search()
        self.getXMLpos()
        for imgPos,xmlPos in tqdm(list(zip(self.imagePos,self.xmlPos)),desc='flip images'):
            self.flipImage(imgPos)
            self.flipXML(xmlPos)
