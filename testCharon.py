from importlib import reload
import charon, time,  training_utils

#Neuron zipped experiment
reload(charon)
x = charon.charon('locustNeurom')
start = time.time()
x.runExperimentAnalysis("/media/dataSSD/cellDetector/zips/ApopotosisInduction#1.zip")
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
x = charon.charon()
x.EXP_DIR = "/media/dataSSD/trainingData/topFly/out (copy)"
x.convertTIF2PNG()
x.imgList = x.getImagePos_search(x.EXP_DIR,'png')

#multiple files
reload(charon)
x = charon.charon('locustHaemo')
x.OUTPUT_DIR='/media/gwdg-backup/BackUp/Debbie/analysed'
fList = x.getImagePos_search(x.ZIP_DIR,'zip')
for file in fList:
    x.runExperimentAnalysis(file)


reload(charon)
x = charon.charon()
x.DETECTION_THRESH =0.33
x.MODEL_NAME='topFly_graph'     
x.analyseMovie("/media/bgeurten/HSMovieKrissy/Group of flies(around 30)/30_09_19/2019-09-30__16_55_47.avi",
            "/media/bgeurten/HSMovieKrissy/Group of flies(around 30)/30_09_19/2019-09-30__16_55_47_ana.avi",
            "/media/bgeurten/HSMovieKrissy/Group of flies(around 30)/30_09_19/2019-09-30__16_55_47.xlsx")



reload(training_utils)

t = training_utils.trainDataCuration()
t.chooseCandidateFiles()
# t.renameLabels() or set dictionary
t.labelChanger = {'deadw': 'dead', 'Live': 'alive', 'lve': 'alive', 'live': 'alive', 'Dead': 'dead', 'livw': 'alive', 'alive': 'alive', 'dead': 'dead'}
t.transfer_trainingData()


reload(training_utils)
g = training_utils.runTrainingGenScripts()
g.run()


reload(training_utils)
lm = training_utils.makelabelMapFile(ids=[1,2],names=['alive','dead'])
lm.printNameIDs()   
lm.writeFile()


reload(training_utils)
cf = training_utils.adaptTFconfigFile()
cf.run()