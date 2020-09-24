from importlib import reload
import charon, time,  training_utils

reload(training_utils)

t = training_utils.trainDataCuration('mosquitoDetector',
                                    '/home/bgeurten/ownCloud/DiegoAIdata/03-05-2020_21-59-04/',
                                    sourceImgType ='png')
t.chooseCandidateFiles()
# t.renameLabelsVerbose() or set dictionary
t.labelChanger = {'male1': 'male 1', 'agression': 'aggression', 'male 2': 'male 2', 'male 1': 'male 1', 'homo courtship': 'homo courtship', 'male2': 'male 2', 'courtship': 'courtship', 'female': 'female'}
t.makeTrainDirs()
t.transfer_trainingData()


reload(training_utils)
g = training_utils.runTrainingGenScripts(t)
g.run()

