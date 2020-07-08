from importlib import reload
import charon, time,  training_utils

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