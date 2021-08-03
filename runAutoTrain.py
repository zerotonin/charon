from numpy.core.einsumfunc import _parse_possible_contraction
from autoTrainDataHough import circleDetector,drosoImgSplitter
import os
import numpy as np

parentDir = '/media/dataSSD/labledData/trainData_drosoCell/'
#dS = drosoImgSplitter(parentDir)
#dS.splitImageDir()
stackDirs = [x[0] for x in os.walk(parentDir)]
stackDirs = stackDirs[1::]

'''
cD = circleDetector()
cD.houghMinR          = 2
cD.houghMaxR          = 10
cD.houghMinDist       = 10
imgFiles = [os.path.join(stackDirs[1],f) for f in os.listdir(stackDirs[1]) if f.endswith('png')]
cD.splitCellsInFile(imgFiles[123],plotFlag=False)
'''


cD = circleDetector()

cD.splitCellsInFolder(stackDirs[0],'png')
#cD.saveFolderDF(f'{stackDirs[0]}.csv')
cD.splitCellsInFolder(stackDirs[2],'png')
#cD.saveFolderDF(f'{stackDirs[2]}.csv')

cD.setPrePupaParameters()

cD.splitCellsInFolder(stackDirs[1],'png')
#cD.saveFolderDF(f'{stackDirs[1]}.csv')
cD.splitCellsInFolder(stackDirs[3],'png')
#cD.saveFolderDF(f'{stackDirs[3]}.csv')