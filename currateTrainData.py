import imageio,os
from matplotlib.pyplot import show
import numpy as np
import pandas as pd
import imgaug as ia
from charonListManager import charonListManager 
from boundingBoxHandler import boundingBoxHandler
from tqdm import tqdm
from imgaug.augmentables.bbs import BoundingBoxesOnImage
from imgaug import augmenters as iaa
from xmlHandler import xmlHandler


class curateTrainData:

    def __init__(self,sourceDir,minArea):
        self.sourceDir = sourceDir
        self.minArea = minArea

        #managers
        self.listManager = charonListManager(sourceDir,'png','xml')
        self.xmlManager  = xmlHandler()
        self.bbManager   = boundingBoxHandler()


    def readDataSet(self,fileI):
        xmlPos  = self.xmlFileList[fileI]
        xmlData = self.xmlManager.readXML(xmlPos)
        return xmlData

   
    
    def remove_too_small(self,bbs):
        boolArray = list()
        labelArray = list()
        for bb in bbs:
            if bb.area < self.minArea:
                bb.x1,bb.x2,bb.y1,bb.y2 = [-1,-1,-1,-1]
        
        return bbs.remove_out_of_image(fully=True,partly=True)

    def main(self):
        self.imgFileList, self.xmlFileList = self.listManager.get_xml_img_filepairs()

        for fileI in tqdm(range(len(self.imgFileList)),desc='splitting files'):
            xmlData = self.readDataSet(fileI)


            column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
            file_df     = pd.DataFrame(xmlData, columns=column_name ) 
            bbs = self.bbManager.imageDF_to_bboxArray(file_df)
            bbs = bbs.clip_out_of_image()
            bbs = self.remove_too_small(bbs)
            print(bbs)
        
            
            #self.writeOut(bbs)

    def writeXML(self,curratedDF):
        objectList =list()
        for i,row in curratedDF.iterrows():
            objectList.append((row['class'],[row['xmin'],row['ymin'],row['xmax'],row['ymax']]))
        imageSize = [row['width'],row['height'],3]
        self.xmlManager.create_xml(os.path.join(self.sourceDir,row['filename']),imageSize,objectList,self.sourceDir)
        
    def writeOut(self,bbs_cur,fileI):
        curratedDF = self.bbManager.create_augImageDF(bbs_cur,self.imgFileList[fileI],None,None)
        curratedDF = curratedDF.dropna()
        self.writeXML(curratedDF)


sourceDir = '/media/dataSSD/trainingData/penguinAug/train'
smatd =curateTrainData(sourceDir,50)
smatd.main()
sourceDir = '/media/dataSSD/trainingData/penguinAug/test'

smatd =curateTrainData(sourceDir,100)
smatd.main()