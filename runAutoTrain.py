from numpy.core.einsumfunc import _parse_possible_contraction
from autoTrainDataHough import circleDetector,drosoImgSplitter
import os
import numpy as np

parentDir = '/home/bgeurten/ownCloud/ScienceProjects/Quantification/Stacks/'
#dS = drosoImgSplitter(parentDir)
#dS.splitImageDir()
stackDirs = [x[0] for x in os.walk(parentDir)]
stackDirs = stackDirs[1::]


cD = circleDetector()
cD.houghMinR          = 5
cD.houghMaxR          = 10
cD.houghMinDist       = 4
imgFiles = [os.path.join(stackDirs[1],f) for f in os.listdir(stackDirs[1]) if f.endswith('png')]
cD.detectCellsInFile(imgFiles[123],plotFlag=True)



cD = circleDetector()
for stack in stackDirs[]:
    cD.detectCellsInFolder(stack,'png')
    cD.saveFolderDF(f'{stack}.csv')

cD = circleDetector()
cD.setPrePupaParameters()
cD.detectCellsInFolder(stackDirs[1],'png')
cD.saveFolderDF(f'{stackDirs[1]}.csv')
cD.detectCellsInFolder(stackDirs[3],'png')
cD.saveFolderDF(f'{stackDirs[3]}.csv')