from importlib import reload
import charon, time,  training_utils

reload(training_utils)

t = training_utils.trainDataCuration()
t.WORK_DIR='/media/dataSSD/trainingData/triboliumNeuron/origData'
t.TEST_DIR='/media/dataSSD/trainingData/triboliumNeuron/test'
t.TRAIN_DIR='/media/dataSSD/trainingData/triboliumNeuron/train'
t.sourceImgType ='tif'
t.chooseCandidateFiles()
# t.renameLabelsVerbose() or set dictionary
t.labelChanger = {'male1': 'male 1', 'agression': 'aggression', 'male 2': 'male 2', 'male 1': 'male 1', 'homo courtship': 'homo courtship', 'male2': 'male 2', 'courtship': 'courtship', 'female': 'female'}
t.transfer_trainingData()


reload(training_utils)
g = training_utils.runTrainingGenScripts(t,'triboliumNeuron')
g.run()

