
import pandas as pd
from imgaug.augmentables.bbs import BoundingBoxesOnImage

class boundingBoxHandler:

    def __init__(self):
        pass

    def renameFile(self,filename,tag,version):
        filename,extension = filename.rsplit('.',1)
        if version:
            return f'{filename}_{tag}_{version}.{extension}'
        else:
            return f'{filename}_{tag}.{extension}'
    
    def bboxArray_to_bboxDF(self, bbs_object): #bbs_obj_to_df
        # function to convert BoundingBoxesOnImage object into DataFrame
        # convert BoundingBoxesOnImage object into array
        bbs_array = bbs_object.to_xyxy_array()
        
        # convert array into a DataFrame ['xmin', 'ymin', 'xmax', 'ymax'] columns
        df_bbs = pd.DataFrame(bbs_array, columns=['xmin', 'ymin', 'xmax', 'ymax'])
        return df_bbs
    
    def imageDF_to_bboxArray(self,group_df,image):#augmentation_groupDF2bbArray
        bb_array_np = group_df.drop(['filename', 'width', 'height', 'class'], axis=1).values
        # pass the array of bounding boxes coordinates to the imgaug library
        bb_array_ia = BoundingBoxesOnImage.from_xyxy_array(bb_array_np, shape=image.shape)
        
        for c,row in group_df.iterrows():
            bb_array_ia[c].label = row['class']

        return bb_array_ia

    def create_augImageDF(self,bbs_aug,imagePos,imageSize,image_suffix,augVersion): #
        # create a data frame with augmented bounding boxes coordinates using the function we created earlier
        bbs_df = self.bboxArray_to_bboxDF(bbs_aug)
        newFileName = self.renameFile(imagePos,image_suffix,augVersion)
        for index, _ in bbs_df.iterrows():
            bbs_df.at[index, 'width'] = imageSize[1]
            bbs_df.at[index, 'height'] = imageSize[0]
            bbs_df.at[index, 'class'] = bbs_aug[index].label
            bbs_df.at[index,'filename'] = newFileName
        # concat all new augmented info into new data frame
        cols = ['filename','width','height','class','xmin', 'ymin', 'xmax', 'ymax']
        return bbs_df