from importlib import reload
import charon, time,  training_utils

reload(training_utils)

t = training_utils.trainDataCuration()
t.WORK_DIR='/media/dataSSD/trainingData/flyBehav/origData'
t.TEST_DIR='/media/dataSSD/trainingData/flyBehav/test'
t.TRAIN_DIR='/media/dataSSD/trainingData/flyBehav/train'
t.sourceImgType ='png'
t.chooseCandidateFiles()
# t.renameLabelsVerbose() or set dictionary
t.labelChanger = {'male1': 'male 1', 'agression': 'aggression', 'male 2': 'male 2', 'male 1': 'male 1', 'homo courtship': 'homo courtship', 'male2': 'male 2', 'courtship': 'courtship', 'female': 'female'}
t.transfer_trainingData()


reload(training_utils)
g = training_utils.runTrainingGenScripts(t,'flyCourtBehav')
g.run()



reload(training_utils)
cf = training_utils.adaptTFconfigFile()
cf.run()