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

reload(training_utils)

t = training_utils.training_utils()
t.chooseCandidateFiles()
x.runExperimentAnalysis("/media/dataSSD/cellDetector/analysing/2020-05-06_Lm-neuron-TRB#1.zip")
end = time.time()
print(end - start)

#read file list trace
reload(charon)
x = charon.charon()
x.getImagePos_readTXT('/media/dataSSD/cellDetector/test1.txt') 
x.runTreatmentAnalysis("/media/dataSSD/cellDetector/PHL neurons #1","test.xls")


# do everything by hand
reload(charon)
x = charon.charon("drosoSocial")
x.EXP_DIR = "/media/dataSSD/trainingData/flyBehav/origData/test4AI"
#x.convertTIF2PNG()
x.imgList = x.getImagePos_search(x.EXP_DIR,'png')
x.runTreatmentAnalysis("/media/dataSSD/trainingData/flyBehav/origData/test4AI","test.xls")    

#multiple files
reload(charon)
x = charon.charon('locustHaemo')
x.OUTPUT_DIR='/media/gwdg-backup/BackUp/Debbie/analysed'
fList = x.getImagePos_search(x.ZIP_DIR,'zip')
for file in fList:
    x.runExperimentAnalysis(file)

#analyse movie
reload(charon)
x = charon.charon('drosoSocial')
x.DETECTION_THRESH =0.75  
x.analyseMovie("/home/bgeurten/Aitest/2018_11_22_mix_dark_5min.mkv", #moviePos
            "/home/bgeurten/Aitest/ana/test.avi", #anaPath out
            "/home/bgeurten/Aitest/ana/test.xlsx") # xlsx file


