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

def sendDirToTSP(sourceDir,fileExt,AIstring,detThresh,writeMovFlag,pythonPos='/home/bgeurten/anaconda3/envs/charon/bin/python',charonDir = '/home/bgeurten/PyProjects/charon'):
    fileList = recursiveFindFiles(sourceDir,fileExt)
    for f in fileList:
        os.system(f'')
        os.system(f'tsp cd {charonDir}; {pythonPos} charonMovieToTSP.py -i {f} -a {AIstring} -d {detThresh} -o {writeMovFlag}')


sourceDir    = '/media/gwdg-backup/BackUp/penguins/'
fileExt      = 'mp4'
AIstring     = 'penguinPicker'
detThresh    = 0.95
writeMovFlag = False

sendDirToTSP(sourceDir,fileExt,AIstring,detThresh,writeMovFlag)