import pandas as pd
from imgaug.augmentables.bbs import BoundingBoxesOnImage

class boundingBoxHandler:

    def __init__(self):
        pass

    def renameFile(self,filename,tag,version):
        filename,extension = filename.rsplit('.',1)
        return f'{filename}_{tag}_{version}.{extension}'
    
    def bboxArray_to_bboxDF(self, bbs_object): #bbs_obj_to_df
        # function to convert BoundingBoxesOnImage object into DataFrame
        # convert BoundingBoxesOnImage object into array
        bbs_array = bbs_object.to_xyxy_array()
        # convert array into a DataFrame ['xmin', 'ymin', 'xmax', 'ymax'] columns
        df_bbs = pd.DataFrame(bbs_array, columns=['xmin', 'ymin', 'xmax', 'ymax'])
        return df_bbs
    
    def imageDF_to_bboxArray(self,group_df,image):#augmentation_groupDF2bbArray
        bb_array = group_df.drop(['filename', 'width', 'height', 'class'], axis=1).values
        #   pass the array of bounding boxes coordinates to the imgaug library
        return BoundingBoxesOnImage.from_xyxy_array(bb_array, shape=image.shape)

    def create_augImageDF(self,group_df,image_aug,image_suffix,bbs_aug,augVersion): #
        # create a data frame with augmented values of image width and height
        info_df = group_df.drop(['xmin', 'ymin', 'xmax', 'ymax'], axis=1)        
        for index, _ in info_df.iterrows():
            info_df.at[index, 'width'] = image_aug.shape[1]
            info_df.at[index, 'height'] = image_aug.shape[0]

        # rename filenames by adding the predifined prefix
        info_df['filename'] = info_df['filename'].apply(lambda x: self.renameFile(x,image_suffix,augVersion))
        # create a data frame with augmented bounding boxes coordinates using the function we created earlier
        bbs_df = self.bboxArray_to_bboxDF(bbs_aug)
        # concat all new augmented info into new data frame
        return pd.concat([info_df, bbs_df], axis=1)