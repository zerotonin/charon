import os 

def recursiveFindFiles(sourceDir,fileExt):
    '''
    Find all files with a user defined extension in folder recursively.
    '''
    os.system('clear')
    print('Finding Files!')
    fileList =  [os.path.join(dp, f) for dp, dn, filenames in os.walk(sourceDir) for f  in filenames if f.endswith(fileExt)]
    fileList.sort()
    return fileList

def sendMovDirToTSP4Charon(sourceDir,fileExt,AIstring,detThresh,writeMovFlag,pythonPos='/home/bgeurten/anaconda3/envs/charon/bin/python',charonDir = '/home/bgeurten/PyProjects/charon'):
    fileList = recursiveFindFiles(sourceDir,fileExt)
    for f in fileList:
        os.system(f'tsp cd {charonDir}')
        os.system(f'tsp {pythonPos} charonMovieToTSP.py -i {f} -a {AIstring} -d {detThresh} -o {writeMovFlag}')


def sendMovieToTSP4Splitting(moviePos,pythonPos='/home/bgeurten/anaconda3/envs/mediaManager/bin/python',mmDir = '/home/bgeurten/PyProjects/mediamanager'):
    os.system(f'tsp cd {mmDir}')
    os.system(f'tsp {pythonPos} food54ArenaSplitter.py -i {moviePos}')

def getSplitDir(movPos):
    # make output objects
    path         = os.path.dirname(movPos)
    fileName     = os.path.basename(movPos).split('.')
    return os.path.join(path,fileName[0])
    
## Kenneth
#sourceDir    = '/media/gwdg-backup/BackUp/penguins/'
#fileExt      = 'mp4'
#AIstring     = 'penguinPicker'
#detThresh    = 0.95
#writeMovFlag = False
#
#sendDirToTSP(sourceDir,fileExt,AIstring,detThresh,writeMovFlag)

# Yegi
sourceDir    = r'/media/gwdg-backup/BackUp/Lennart/'
fileExt      = 'mp4'
AIstring     = 'flyFinder24hBorderless'
detThresh    = 0.95
writeMovFlag = False


movList = recursiveFindFiles(sourceDir,fileExt)
for mov in movList:
    sendMovieToTSP4Splitting(mov)
    sendMovDirToTSP4Charon(getSplitDir(mov),fileExt,AIstring,detThresh,writeMovFlag)