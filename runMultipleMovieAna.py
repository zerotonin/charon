from importlib import reload
import charon, time,  training_utils
from tqdm import tqdm

reload(charon)
x = charon.charon('flyFinder')
x.DETECTION_THRESH =0.75  
# folders that need to be investigated
folderList = ["/media/gwdg-backup/BackUp/Anka/Anka00",
              "/media/gwdg-backup/BackUp/Anka/Anka01",
              "/media/gwdg-backup/BackUp/Anka/Anka02",
              "/media/gwdg-backup/BackUp/Anka/Anka03",
              "/media/gwdg-backup/BackUp/Anka/Anka04",
              "/media/gwdg-backup/BackUp/Anka/Anka05",
              "/media/gwdg-backup/BackUp/Anka/Anka06",
              "/media/gwdg-backup/AutoBenzerSwap"]
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
for file in tqdm(fileList,desc='analysing movies '):

    x.analyseMovie(file, #moviePos
            file[0:-4]+'_ana.avi', #anaPath out
            file[0:-3]+'tra',writeDetectionMov=True) # tra file