from importlib import reload
import charon, time, os
from tqdm import tqdm


#Neuron zipped experiment
reload(charon)
x = charon.charon('drosoNucleus')
start = time.time()
x.runExperimentAnalysis("/media/dataSSD/drosoTestStackExp.zip")
end = time.time()
print(end - start)


#Haemo zipped experiment
reload(charon)
x = charon.charon('locustHaemo')
start = time.time()
x.runExperimentAnalysis("/media/gwdg-backup/BackUp/Debbie/cellAna_new/Neuron Test #1.zip")
end = time.time()
print(end - start)

#read file list trace
reload(charon)
x = charon.charon()
x.getImagePos_readTXT('/media/dataSSD/cellDetector/test1.txt') 
x.runTreatmentAnalysis("/media/dataSSD/cellDetector/PHL neurons #1","test.xls")


# do everything by hand
reload(charon)
x = charon.charon("drosoCellCounting")
x.EXP_DIR = "/home/bgeurten/Downloads/Test-pictures"
#x.convertTIF2PNG()
x.imgList = x.getImagePos_search(x.EXP_DIR,'tif')
x.runTreatmentAnalysis("/home/bgeurten/Downloads/Test-pictures","test.xls")    

#multiple files
reload(charon)
x = charon.charon('triboliumNeuron')
#x.OUTPUT_DIR='/media/gwdg-backup/BackUp/Debbie/analysed'
fList = x.getImagePos_search(x.ZIP_DIR,'zip')
for file in fList:
    x.runExperimentAnalysis(file)

#analyse movie
reload(charon)
x = charon.charon('flyFinder24hBorderless')
x.DETECTION_THRESH =0.75  
start = time.time()

#'/media/gwdg-backup/BackUp/KathyBrands/MasterVideos/2020-10-16__15_47_00_yellowRut7_yellowgreen_IR.avi'
#'/media/gwdg-backup/BackUp/KathyBrands/MasterVideos/2020-10-16__16_20_02_yellowRut7_yellowgreen_Light.avi'

x.DETECTION_THRESH =0.5  
x.analyseMovie('/media/gwdg-backup/BackUp/Lennart/2021-10-03_10-19-27.mp4', #moviePos
            "/home/bgeurten/Videos/test_IR_05.avi", #anaPath out
            "/home/bgeurten/Videos/test_IR_05.tra", writeDetectionMov=True) # trace file

end = time.time()
print(end - start)
# Diego Test 1
#start = 2020-10-01 17:28:10.578095
#end   = 2020-10-01 18:59:55 


#analyse multiple movie
reload(charon)
x = charon.charon('triboliumTracer4x')
x.DETECTION_THRESH =0.8

aviList = x.getImagePos_search('/media/gwdg-backup/BackUp/Yegi','avi')
traList = x.getImagePos_search('/media/gwdg-backup/BackUp/Yegi','tra')
traList = [os.path.basename(x)[:-4] for x in traList]
delList = list()
for aviFile in tqdm(aviList):
    if os.path.basename(aviFile)[:-4] in traList:
        print(aviFile)
        aviList.remove(aviFile)


#fList = fList+ x.getImagePos_search('/home/bgeurten/Videos/testVideos/manuBenzer','mp4')
for file in tqdm(aviList):
    try:
        x.analyseMovie(file, #moviePos
            file[0:-4]+'_ana.avi', #anaPath out
            file[0:-3]+'tra', writeDetectionMov=False) # xlsx file
    except:
        print(f'following file unreadable: {file}' )

# analyse single movie  
reload(charon)
x = charon.charon('triboliumTracer4x')
x.DETECTION_THRESH =0.5  
file='/media/gwdg-backup/BackUp/Yegi/2020-11-19__14_34_03.avi'
x.analyseMovie(file, #moviePos
            file[0:-4]+'_ana.avi', #anaPath out
            file[0:-3]+'tra', writeDetectionMov=True) # xlsx file

# analyse single movie  
reload(charon)
x = charon.charon('penguinPicker')
x.DETECTION_THRESH =0.95  
file='/media/gwdg-backup/BackUp/penguins/Gentoo/Gentoo_04-03-2021.mp4'
x.analyseMovie(file, #moviePos
            file[0:-4]+'_ana.avi', #anaPath out
            file[0:-3]+'tra', writeDetectionMov=True) # xlsx file

# analyse single movie  
reload(charon)
x = charon.charon('flyFinder_manuBenzer')
x.DETECTION_THRESH =0.25  
file='/media/gwdg-backup/AutoBenzerSwap/2020-06-06__17_46_43.avi'
x.analyseMovie(file, #moviePos
            file[0:-4]+'_ana.avi', #anaPath out
            file[0:-3]+'tra', writeDetectionMov=True) # xlsx file

import os

for f in fileList:
    os.system(f'tsp ' + str(f))
#analyse multiple movie
reload(charon)
x = charon.charon('triboliumTracer4x')
x.DETECTION_THRESH =0.8

fList = x.getImagePos_search('/media/gwdg-backup/BackUp/Yegi','avi')
#fList = fList+ x.getImagePos_search('/home/bgeurten/Videos/testVideos/manuBenzer','mp4')
for file in fList:
    x.analyseMovie(file, #moviePos
            file[0:-4]+'_ana.avi', #anaPath out
            file[0:-3]+'tra', writeDetectionMov=False) # xlsx file