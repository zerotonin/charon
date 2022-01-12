from io import BufferedIOBase
import re,os,glob,shutil,cv2,imageio
import imgaug as ia
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
from imgaug import augmenters as iaa
from charonListManager import charonListManager 
from tqdm import tqdm
from dataframe2labelImgXML import dataframe2labelImgXML
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET

class imgaug4charon:

    def __init__(self,sourceDir,imgExt,dataExt,targetDir):
        self.sourceDir = sourceDir
        self.imgExt    = imgExt
        self.dataExt   = dataExt
        self.targetDir = targetDir

        # preallocations
        self.imgFileList = list()
        self.xmlFileList = list()
        
        self.sometimes = lambda aug: iaa.Sometimes(0.5, aug)
        # main augmentor
        self.mainAugmentorSeq = iaa.Sequential(
            [
                # apply the following augmenters to most images
                iaa.Fliplr(0.5), # horizontally flip 50% of all images
                iaa.Flipud(0.2), # vertically flip 20% of all images
                # crop images by -5% to 10% of their height/width
                self.sometimes(iaa.CropAndPad(
                    percent=(-0.05, 0.1),
                    pad_mode=ia.ALL,
                    pad_cval=(0, 255)
                )),
                self.sometimes(iaa.Affine(
                    scale={"x": (0.8, 1.2), "y": (0.8, 1.2)}, # scale images to 80-120% of their size, individually per axis
                    translate_percent={"x": (-0.2, 0.2), "y": (-0.2, 0.2)}, # translate by -20 to +20 percent (per axis)
                    rotate=(-45, 45), # rotate by -45 to +45 degrees
                    shear=(-16, 16), # shear by -16 to +16 degrees
                    order=[0, 1], # use nearest neighbour or bilinear interpolation (fast)
                    cval=(0, 255), # if mode is constant, use a cval between 0 and 255
                    mode=ia.ALL#['constant','edge'] # use any of scikit-image's warping modes (see 2nd image from the top for examples)
                )),
                # execute 0 to 5 of the following (less important) augmenters per image
                # don't execute all of them, as that would often be way too strong
                iaa.SomeOf((0, 5),
                    [
                        self.sometimes(iaa.Superpixels(p_replace=(0, 1.0), n_segments=(20, 200))), # convert images into their superpixel representation
                        iaa.OneOf([
                            iaa.GaussianBlur((0, 3.0)), # blur images with a sigma between 0 and 3.0
                            iaa.AverageBlur(k=(2, 7)), # blur image using local means with kernel sizes between 2 and 7
                            iaa.MedianBlur(k=(3, 11)), # blur image using local medians with kernel sizes between 2 and 7
                        ]),
                        iaa.Sharpen(alpha=(0, 1.0), lightness=(0.75, 1.5)), # sharpen images
                        iaa.Emboss(alpha=(0, 1.0), strength=(0, 2.0)), # emboss images
                        # search either for all edges or for directed edges,
                        # blend the result with the original image using a blobby mask
                        iaa.BlendAlphaSimplexNoise(iaa.OneOf([
                            iaa.EdgeDetect(alpha=(0.5, 1.0)),
                            iaa.DirectedEdgeDetect(alpha=(0.5, 1.0), direction=(0.0, 1.0)),
                        ])),
                        iaa.AdditiveGaussianNoise(loc=0, scale=(0.0, 0.05*255), per_channel=0.5), # add gaussian noise to images
                        iaa.OneOf([
                            iaa.Dropout((0.01, 0.1), per_channel=0.5), # randomly remove up to 10% of the pixels
                            iaa.CoarseDropout((0.03, 0.15), size_percent=(0.02, 0.05), per_channel=0.2),
                        ]),
                        iaa.Invert(0.05, per_channel=True), # invert color channels
                        iaa.Add((-10, 10), per_channel=0.5), # change brightness of images (by -10 to 10 of original value)
                        iaa.AddToHueAndSaturation((-20, 20)), # change hue and saturation
                        # either change the brightness of the whole image (self.sometimes
                        # per channel) or change the brightness of subareas
                        iaa.OneOf([
                            iaa.Multiply((0.5, 1.5), per_channel=0.5),
                            iaa.FrequencyNoiseAlpha(
                                exponent=(-4, 0),
                                first=iaa.Multiply((0.5, 1.5), per_channel=True),
                                second=iaa.LinearContrast((0.5, 2.0))
                            )
                        ]),
                        iaa.LinearContrast((0.5, 2.0), per_channel=0.5), # improve or worsen the contrast
                        iaa.Grayscale(alpha=(0.0, 1.0)),
                        self.sometimes(iaa.ElasticTransformation(alpha=(0.5, 3.5), sigma=0.25)), # move pixels locally around (with random strengths)
                        self.sometimes(iaa.PiecewiseAffine(scale=(0.01, 0.05))), # self.sometimes move parts of the image around
                        self.sometimes(iaa.PerspectiveTransform(scale=(0.01, 0.1)))
                    ],
                    random_order=True
                )
            ],
            random_order=True
        )
        self.xmlWriter = dataframe2labelImgXML()
        if not os.path.exists(self.targetDir):
            os.makedirs(self.targetDir)

    def getXMLdata(self,xml_file):
        xml_list = list()
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            value = (root.find('filename').text,
                        int(root.find('size')[0].text),
                        int(root.find('size')[1].text),
                        member[0].text,
                        int(member[4][0].text),
                        int(member[4][1].text),
                        int(member[4][2].text),
                        int(member[4][3].text)
                        )
            xml_list.append(value)
        return xml_list

    def getAllDetInDir(self):
        allXML=list()

        for file in self.xmlFileList:
            allXML += self.getXMLdata(file)
        
        column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
        return pd.DataFrame(allXML, columns=column_name) 

    def getGroup(self,groupID):
        group_df = self.labelDF_fName.get_group(groupID)
        group_df = group_df.reset_index()
        group_df = group_df.drop(['index'], axis=1)
        return group_df

    def getSourceFilePos(self,fileName):
        return os.path.join(self.sourceDir,fileName)
    
    def renameFile(self,filename,tag,version):
        filename,extension = filename.rsplit('.',1)
        return f'{filename}_{tag}_{version}.{extension}'

    
    def showSourceLabels(self,image,group_df):
        classes = group_df['class'].values
        bb_array = group_df.drop(['filename', 'width', 'height', 'class'], axis=1).values
        bbs = BoundingBoxesOnImage.from_xyxy_array(bb_array, shape=self.imageList[-1].shape,)
        c = 0
        for bb in bbs:
            bb.label = classes[c]
            c+=1
        ia.imshow(bbs.draw_on_image(image, size=2))

    def bbs_obj_to_df(self, bbs_object):
        # function to convert BoundingBoxesOnImage object into DataFrame
        # convert BoundingBoxesOnImage object into array
        bbs_array = bbs_object.to_xyxy_array()
        # convert array into a DataFrame ['xmin', 'ymin', 'xmax', 'ymax'] columns
        df_bbs = pd.DataFrame(bbs_array, columns=['xmin', 'ymin', 'xmax', 'ymax'])
        return df_bbs

    
    def augmentation_groupDF2bbArray(self,group_df,image):
        bb_array = group_df.drop(['filename', 'width', 'height', 'class'], axis=1).values
        #   pass the array of bounding boxes coordinates to the imgaug library
        return BoundingBoxesOnImage.from_xyxy_array(bb_array, shape=image.shape)

    def augmentation_createAugBBs(self,group_df,image_aug,image_suffix,bbs_aug,augVersion):
        # create a data frame with augmented values of image width and height
        info_df = group_df.drop(['xmin', 'ymin', 'xmax', 'ymax'], axis=1)        
        for index, _ in info_df.iterrows():
            info_df.at[index, 'width'] = image_aug.shape[1]
            info_df.at[index, 'height'] = image_aug.shape[0]

        # rename filenames by adding the predifined prefix
        info_df['filename'] = info_df['filename'].apply(lambda x: self.renameFile(x,image_suffix,augVersion))
        # create a data frame with augmented bounding boxes coordinates using the function we created earlier
        bbs_df = self.bbs_obj_to_df(bbs_aug)
        # concat all new augmented info into new data frame
        return pd.concat([info_df, bbs_df], axis=1)
    
    def augmentation_iniSizeAug(self,fixSize):
        # height augmentor
        self.height_resize = iaa.Sequential([ 
                        iaa.Resize({"height": fixSize, "width": 'keep-aspect-ratio'})])
        #width augmentor
        self.width_resize = iaa.Sequential([ 
                        iaa.Resize({"height": 'keep-aspect-ratio', "width": fixSize})])

    def resize_imgaug(self, group_df,image,bbs,fixSize=600):

        self.augmentation_iniSizeAug(fixSize)
        # If image height is greater than or equal to image width 
        #   AND greater than 600px perform resizing augmentation shrinking image height to 600px.
        if group_df['height'].unique()[0] >= group_df['width'].unique()[0] and group_df['height'].unique()[0] > 600:
            #apply augmentation on image and on the bounding boxes
            image_aug, bbs_aug = self.height_resize(image=image, bounding_boxes=bbs)        

        #  if image width is greater than image height 
        #  AND greater than 600px perform resizing augmentation shrinking image width to 600px
        elif group_df['width'].unique()[0] > group_df['height'].unique()[0] and group_df['width'].unique()[0] > 600:
            #   apply augmentation on image and on the bounding boxes
            image_aug, bbs_aug = self.width_resize(image=image, bounding_boxes=bbs)
        

        # append image info without any changes if it's height and width are both less than 600px 
        else:
            bbs_aug = self.augmentation_groupDF2bbArray(group_df,image)
        return image_aug, bbs_aug

    def mainAugmentation(self,augSeeds=5,fixSize = 0,tag ='aug'):
        # create data frame which we're going to populate with augmented image info
        output_BBS_DF = pd.DataFrame(columns=
                                ['filename','width','height','class', 'xmin', 'ymin', 'xmax', 'ymax']
                                )
        c = 0
        for filePos in tqdm(self.imgFileList,desc=f'augmentation'):
            image = imageio.imread(filePos)
            filename = os.path.basename(filePos)
            # Get separate data frame grouped by file name
            group_df = self.getGroup(filename)
            # Get the image and bounding box data
            bbs = self.augmentation_groupDF2bbArray(group_df,image)


            if fixSize > 0:
                image,bbs = self.resize_imgaug(group_df,image,bbs,fixSize)
                imageio.imwrite(os.path.join(self.targetDir,self.renameFile(filename,'orig',0)), image)  
                resize_df = self.augmentation_createAugBBs(group_df,image,'orig',bbs,0)
                self.writeXML(resize_df)
                #append rows to output_BBS_DF data frame
                output_BBS_DF = pd.concat([output_BBS_DF, resize_df])
            
            augVersion = 0
            while augVersion < augSeeds:
                # main augmentation
                image_aug, bbs_aug =self.mainAugmentorSeq(image=image, bounding_boxes=bbs)
                bbs_aug = bbs_aug.remove_out_of_image(fully=True,partly=False)
                aug_df = self.augmentation_createAugBBs(group_df,image_aug,tag,bbs_aug,augVersion)
                aug_df = aug_df.dropna()
                if aug_df.shape[0]>0:
                    # append rows to output_BBS_DF data frame
                    output_BBS_DF = pd.concat([output_BBS_DF, aug_df])
                    #write new xml-file
                    self.writeXML(aug_df)               # write augmented image
                    imageio.imwrite(os.path.join(self.targetDir,self.renameFile(filename,tag,augVersion)), image_aug) 
                    augVersion+=1 
            c+=1
        # return dataframe with updated images and bounding boxes annotations 
        output_BBS_DF = output_BBS_DF.reset_index()
        output_BBS_DF = output_BBS_DF.drop(['index'], axis=1)
        return output_BBS_DF
    
    def writeXML(self,aug_df):
        objectList =list()
        for i,row in aug_df.iterrows():
            objectList.append((row['class'],[row['xmin'],row['ymin'],row['xmax'],row['ymax']]))
        imageSize = [row['width'],row['height'],3]
        self.xmlWriter.create_xml(os.path.join(self.targetDir,row['filename']),imageSize,objectList,self.targetDir)


    def main(self, augSeeds=5, fixSize=0):

        self.listManager = charonListManager(self.sourceDir,self.imgExt,'xml')
        self.imgFileList, self.xmlFileList = self.listManager.get_xml_img_filepairs()
        self.labelDF       = self.getAllDetInDir()
        self.labelDF_fName = self.labelDF.groupby('filename')
        self.augDF = self.mainAugmentation(augSeeds,fixSize)
        self.augDF_fName = self.augDF.groupby('filename')


parentDir = '/media/dataSSD/labledData/trainData_penguin'
targetDir = '/media/dataSSD/labledData/trainData_penguinAug'

ia4c = imgaug4charon(parentDir,'png','xml',targetDir)
ia4c.main(10,1000)
#ia4c.showSourceLabels(7)
ia4c.augDF_fName = ia4c.augDF.groupby('filename')