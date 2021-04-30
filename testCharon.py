from importlib import reload
import charon, time,  training_utils

#Neuron zipped experiment
reload(charon)
x = charon.charon('locustNeuron')
start = time.time()
x.runExperimentAnalysis("/media/dataSSD/ownCloudDrosoVis/cellDetector_charon/upload/locustNeuron/2021-04-22_Lm-neuron-Rotenon-12h-2.zip")
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
x = charon.charon('flyFinder')
x.DETECTION_THRESH =0.75  
start = time.time()

#'/media/gwdg-backup/BackUp/KathyBrands/MasterVideos/2020-10-16__15_47_00_yellowRut7_yellowgreen_IR.avi'
#'/media/gwdg-backup/BackUp/KathyBrands/MasterVideos/2020-10-16__16_20_02_yellowRut7_yellowgreen_Light.avi'

x.DETECTION_THRESH =0.5  
x.analyseMovie('/media/gwdg-backup/BackUp/KathyBrands/MasterVideos/2020-10-16__15_47_00_yellowRut7_yellowgreen_IR.avi', #moviePos
            "/home/bgeurten/Videos/test_IR_05.avi", #anaPath out
            "/home/bgeurten/Videos/test_IR_05.tra", writeDetectionMov=True) # trace file
x.DETECTION_THRESH =0.25  
x.analyseMovie('/media/gwdg-backup/BackUp/KathyBrands/MasterVideos/2020-10-16__15_47_00_yellowRut7_yellowgreen_IR.avi', #moviePos
            "/home/bgeurten/Videos/test_IR_025.avi", #anaPath out
            "/home/bgeurten/Videos/test_IR_025.tra", writeDetectionMov=True) # trace file
x.DETECTION_THRESH =0.75  
x.analyseMovie('/media/gwdg-backup/BackUp/KathyBrands/MasterVideos/2020-10-16__16_20_02_yellowRut7_yellowgreen_Light.avi', #moviePos
            "/home/bgeurten/Videos/test_VL_075.avi", #anaPath out
            "/home/bgeurten/Videos/test_VL_075.tra", writeDetectionMov=True) # trace file
x.DETECTION_THRESH =0.5  
x.analyseMovie('/media/gwdg-backup/BackUp/KathyBrands/MasterVideos/2020-10-16__16_20_02_yellowRut7_yellowgreen_Light.avi', #moviePos
            "/home/bgeurten/Videos/test_VL_05.avi", #anaPath out
            "/home/bgeurten/Videos/test_VL_05.tra", writeDetectionMov=True) # trace file
x.DETECTION_THRESH =0.25  
x.analyseMovie('/media/gwdg-backup/BackUp/KathyBrands/MasterVideos/2020-10-16__16_20_02_yellowRut7_yellowgreen_Light.avi', #moviePos
            "/home/bgeurten/Videos/test_VL_025.avi", #anaPath out
            "/home/bgeurten/Videos/test_VL_025.tra", writeDetectionMov=True) # trace file
end = time.time()
print(end - start)
# Diego Test 1
#start = 2020-10-01 17:28:10.578095
#end   = 2020-10-01 18:59:55 


#analyse multiple movie
reload(charon)
x = charon.charon('flyFinder_manuBenzer')
x.DETECTION_THRESH =0.5  

fList = x.getImagePos_search('/home/bgeurten/Videos/testVideos/manuBenzer','avi')
fList = fList+ x.getImagePos_search('/home/bgeurten/Videos/testVideos/manuBenzer','mp4')
for file in fList:
    x.analyseMovie(file, #moviePos
            file[0:-4]+'_ana.avi', #anaPath out
            file[0:-3]+'tra', writeDetectionMov=True) # xlsx file