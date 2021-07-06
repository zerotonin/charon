from autoTrainDataHough import circleDetector
import os

parentDir = '/home/bgeurten/ownCloud/ScienceProjects/Quantification/Stacks/'
stackDirs = [x[0] for x in os.walk(parentDir)]
stackDirs = stackDirs[1::]


cD = circleDetector()
for stack in stackDirs:
    cD.detectCellsInFolder(stack,'png')
    cD.saveFolderDF(f'{stack}.csv')