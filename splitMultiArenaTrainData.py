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


class splitLabelAutoBenzer:

    def __init__(self,sourceDir,targetDir):
        self.sourceDir = sourceDir
        self.targetDir = targetDir

        #managers
        self.listManager = charonListManager(sourceDir,'png','xml')
        self.xmlManager  = xmlHandler()
        self.bbManager   = boundingBoxHandler()

        #augmentors
        self.augTopLeft  = iaa.Crop(percent=(0,.5,.5,0))
        self.augBotLeft  = iaa.Crop(percent=(.5,.5,0,0))
        self.augBotRight = iaa.Crop(percent=(.5,0,0,.5))
        self.augTopRight = iaa.Crop(percent=(0,0,0.5,.5))

        if not os.path.exists(self.targetDir):
            os.makedirs(self.targetDir)


    def ensureRGB(self,image):
        if len(image.shape) < 3:
            return np.stack((image,)*3, axis=-1)
        else:
            return image
    def showSourceLabels(self,image,group_df):
        classes = group_df['class'].values
        bb_array = group_df.drop(['filename', 'width', 'height', 'class'], axis=1).values
        bbs = BoundingBoxesOnImage.from_xyxy_array(bb_array, shape=image.shape)
        c = 0
        for bb in bbs:
            bb.label = classes[c]
            c+=1
        ia.imshow(bbs.draw_on_image(image, size=2)) 

    def readDataSet(self,fileI):
        imgPos = self.imgFileList[fileI]
        image  = imageio.imread(imgPos)
        image  = self.ensureRGB(image)

        xmlPos  = self.xmlFileList[fileI]
        xmlData = self.xmlManager.readXML(xmlPos)
        return image,xmlData

    def writeXML(self,aug_df):
        objectList =list()
        for i,row in aug_df.iterrows():
            objectList.append((row['class'],[row['xmin'],row['ymin'],row['xmax'],row['ymax']]))
        imageSize = [row['width'],row['height'],3]
        self.xmlManager.create_xml(os.path.join(self.targetDir,row['filename']),imageSize,objectList,self.targetDir)
        
    def writeOut(self,bbs_aug,image_aug,tag,fileI):
        bbs_aug = bbs_aug.remove_out_of_image(fully=True,partly=True)
        split_df = self.bbManager.create_augImageDF(bbs_aug,self.imgFileList[fileI],tag,None)
        split_df = split_df.dropna()
     
        imageio.imwrite(os.path.join(self.targetDir,split_df.at[0,'filename']), image_aug) 
        self.writeXML(split_df)  

    def main(self):
        self.imgFileList, self.xmlFileList = self.listManager.get_xml_img_filepairs()

        for fileI in tqdm(range(len(self.imgFileList)),desc='splitting files'):
            image,xmlData = self.readDataSet(fileI)


            column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
            file_df     = pd.DataFrame(xmlData, columns=column_name ) 
            bbs = self.bbManager.imageDF_to_bboxArray(file_df)

            image_aug,bbs_aug = self.augTopLeft(image=image, bounding_boxes=bbs)
            self.writeOut(bbs_aug,image_aug,'TL',fileI)
            image_aug,bbs_aug = self.augTopRight(image=image, bounding_boxes=bbs)
            self.writeOut(bbs_aug,image_aug,'TR',fileI)
            image_aug,bbs_aug = self.augBotRight(image=image, bounding_boxes=bbs)
            self.writeOut(bbs_aug,image_aug,'BR',fileI)
            image_aug,bbs_aug = self.augBotLeft(image=image, bounding_boxes=bbs)
            self.writeOut(bbs_aug,image_aug,'BL',fileI)

sourceDir = '/media/dataSSD/labledData/trainData_autoBenzer'
targetDir = '/media/dataSSD/labledData/trainData_autoBenzerSplit'

smatd =splitLabelAutoBenzer(sourceDir,targetDir)
smatd.main()