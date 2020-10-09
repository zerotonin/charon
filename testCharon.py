from importlib import reload
import charon, time,  training_utils

#Neuron zipped experiment
reload(charon)
x = charon.charon('locustNeuron')
start = time.time()
x.runExperimentAnalysis("/media/dataSSD/cellDetector/zips/LuizaLocustaNeuron.zip")
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
x = charon.charon('courtDroso')
x.DETECTION_THRESH =0.75  
x.analyseMovie("/media/gwdg-backup/BackUp/Miriam/Bachelor/BA_Movies/2018_11_28/2018_11_28_mix_dark_5min.mkv", #moviePos
            "/home/bgeurten/Videos/test_tracked.avi", #anaPath out
            "/home/bgeurten/Videos/test.xlsx") # xlsx file
# Diego Test 1
#start = 2020-10-01 17:28:10.578095
#end   = 2020-10-01 18:59:55 


#analyse multiple movie
reload(charon)
x = charon.charon('flyBehav')
x.DETECTION_THRESH =0.75  

fList = x.getImagePos_search('/media/gwdg-backup/BackUp/DNB_2020/DarkFlySingle','avi')
for file in fList:
    x.analyseMovie(file, #moviePos
            file[0:-4]+'_ana.mp4', #anaPath out
            file[0:-3]+'xlsx') # xlsx file