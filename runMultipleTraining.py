from importlib import reload
import charon, time,  training_utils
from tqdm import tqdm
   
reload(charon)
x = charon.charon("flyFinder_food54")
x.DETECTION_THRESH =0.5
# folders that need to be investigated
folderList = ["/media/gwdg-backup/BackUp/KathyBrands/MasterVideos/arena54"]
#check files in each folder
fileList = list()
for folder in folderList:
    fList = x.getImagePos_search(folder,'avi')
    fileList = fileList+fList
    fList = x.getImagePos_search(folder,'mp4')
    fileList = fileList+fList

# get rid of allready analysed videos
fileList = [item for item in fileList  if '_ana' not in item]

# run the analysis
for fileI in tqdm(range(len(fileList)),desc='analysing movies '):
    if fileI == 0 or fileI == len(fileList)-1:
        x.analyseMovie(fileList[fileI], #moviePos
            fileList[fileI][0:-4]+'_ana.avi', #anaPath out
            fileList[fileI][0:-3]+'tra',writeDetectionMov=True) # tra file
    else:
        x.analyseMovie(fileList[fileI], #moviePos
            fileList[fileI][0:-4]+'_ana.avi', #anaPath out
            fileList[fileI][0:-3]+'tra',writeDetectionMov=False) # tra file