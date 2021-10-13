from importlib import reload
import charon,cv2,charonPresenter,os
from pathlib import Path
import pandas as pd
from tqdm import tqdm
# do everything by hand
reload(charon)

def recurFileFinder(srcPath,fileExt):
    fileList = list()
    for path in Path(srcPath).rglob(f'*.{fileExt}'):
        fileList.append(str(path))
    return fileList


def getMetaDataFromFilePosition(filePos):
    fileName = os.path.basename(filePos)
    date,hour,genType,imgType = fileName.split('__') 
    hour = int(hour)
    imgType=imgType.split('.')[0]
    imgTypeList = imgType.split('_')
    imgPosInt = int(imgTypeList[0])
    imgPosStr = imgTypeList[1]
    if len(imgTypeList) == 3:
        light = '12h_12h'
    else:
        light = 'dark'
    return date,hour,genType,light,imgPosStr,imgPosInt

#%% analysis
x = charon.charon("funnelFinder")
srcDir = '/media/gwdg-backup/BackUp/Paul_Funnel'
fileList =recurFileFinder(srcDir,'JPG')
data = list()


for fPos in tqdm(fileList,desc='analysing images'):
    image = cv2.imread(fPos)
    boxes,scores,classes = x.generalMultiClassDetection(image)  
    date,hour,genType,light,imgPosStr,imgPosInt =getMetaDataFromFilePosition(fPos)

    detIndex  = list(range(len(boxes)))
    fileIndex =[fPos for x in detIndex]
    metaData = [(date,hour,genType,light,imgPosStr,imgPosInt) for x in detIndex]
    data+= list(zip(fileIndex,detIndex,boxes,scores,classes,metaData))
indices = [[x[0] for x in data ],[x[1] for x in data ]]
rawData = [(x[5][0],x[5][1],x[5][2],x[5][3],x[5][4],x[5][5],x[4],x[3],x[2][0],x[2][1],x[2][2],x[2][3]) for x in data]
columns    = ['date', 'hour', 'genType', 'light', 'imgPosStr', 'imgPosInt', 'label','quality','y_min','x_min','y_max','x_max']
# index 
df = pd.DataFrame(rawData,columns = columns)
df.to_hdf('/media/gwdg-backup/BackUp/Paul_Funnel/resultDataFrame.h5',key='df')

#%% get larval position
os.system(f'/home/bgeurten/anaconda3/envs/charon/bin/python /home/bgeurten/PyProjects/charon/larvaPosAna')



# %%