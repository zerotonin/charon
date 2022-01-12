from io import BufferedIOBase
import os,imageio
import imgaug as ia
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
from imgaug import augmenters as iaa
from charonListManager import charonListManager 
from boundingBoxHandler import boundingBoxHandler
from tqdm import tqdm
from xmlHandler import xmlHandler
import pandas as pd
import numpy as np

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
        self.xmlManager = xmlHandler()
        self.bbManager = boundingBoxHandler()
        if not os.path.exists(self.targetDir):
            os.makedirs(self.targetDir)

    def getAllDetInDir(self):
        allXML=list()

        for file in self.xmlFileList:
            allXML += self.xmlManager.readXML(file)
        
        column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
        return pd.DataFrame(allXML, columns=column_name) 

    def getGroup(self,groupID):
        group_df = self.labelDF_fName.get_group(groupID)
        group_df = group_df.reset_index()
        group_df = group_df.drop(['index'], axis=1)
        return group_df

    def getSourceFilePos(self,fileName):
        return os.path.join(self.sourceDir,fileName)

    def ensureRGB(self,image):
        if len(image.shape) < 3:
            return np.stack((image,)*3, axis=-1)
        else:
            return image
    def showSourceLabels(self,image,group_df):
        classes = group_df['class'].values
        bb_array = group_df.drop(['filename', 'width', 'height', 'class'], axis=1).values
        bbs = BoundingBoxesOnImage.from_xyxy_array(bb_array, shape=image.shape,)
        c = 0
        for bb in bbs:
            bb.label = classes[c]
            c+=1
        ia.imshow(bbs.draw_on_image(image, size=2))


    
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
            bbs_aug = self.bbManager.imageDF_to_bboxArray(group_df)
        return image_aug, bbs_aug

    def mainAugmentation(self,augSeeds=5,fixSize = 0,tag ='aug'):
    
        c = 0
        for filePos in tqdm(self.imgFileList,desc=f'augmentation'):
            image = imageio.imread(filePos)
            image = self.ensureRGB(image)
            filename = os.path.basename(filePos)
            # Get separate data frame grouped by file name
            group_df = self.getGroup(filename)
            # Get the image and bounding box data
            bbs = self.bbManager.imageDF_to_bboxArray(group_df)


            if fixSize > 0:
                image,bbs = self.resize_imgaug(group_df,image,bbs,fixSize)
                imageio.imwrite(os.path.join(self.targetDir,self.bbManager.renameFile(filename,'orig',0)), image)  
                resize_df = self.bbManager.create_augImageDF(bbs,filePos,'orig',0)
                self.writeXML(resize_df)
              
            
            augVersion = 0
            while augVersion < augSeeds:
                # main augmentation
                image_aug, bbs_aug =self.mainAugmentorSeq(image=image, bounding_boxes=bbs)
                bbs_aug = bbs_aug.remove_out_of_image(fully=True,partly=False)
                aug_df = self.bbManager.create_augImageDF(bbs_aug,filePos,tag,augVersion)
                aug_df = aug_df.dropna()
                if aug_df.shape[0]>0:                    
                    #write new xml-file
                    self.writeXML(aug_df)               # write augmented image
                    imageio.imwrite(os.path.join(self.targetDir,self.bbManager.renameFile(filename,tag,augVersion)), image_aug) 
                    augVersion+=1 
            c+=1
    
    
    def writeXML(self,aug_df):
        objectList =list()
        for i,row in aug_df.iterrows():
            objectList.append((row['class'],[row['xmin'],row['ymin'],row['xmax'],row['ymax']]))
        imageSize = [row['width'],row['height'],3]
        self.xmlManager.create_xml(os.path.join(self.targetDir,row['filename']),imageSize,objectList,self.targetDir)


    def main(self, augSeeds=5, fixSize=0):

        self.listManager = charonListManager(self.sourceDir,self.imgExt,'xml')
        self.imgFileList, self.xmlFileList = self.listManager.get_xml_img_filepairs()
        self.labelDF       = self.getAllDetInDir()
        self.labelDF_fName = self.labelDF.groupby('filename')
        self.mainAugmentation(augSeeds,fixSize)
       


