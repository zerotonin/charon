from importlib import reload

import charon, time,  training_utils, imgaug4charon



reload(training_utils)
path2labeledData = '/media/dataSSD/labledData/trainData_autoBenzerSplit'
path2augmentedData = '/media/dataSSD/labledData/trainData_autoBenzerAug'
nameOfTheNN = 'autoBenzerAug'
maxImageSize = 1024
numofAugClones = 10
imgExt = 'png'


ia4c = imgaug4charon.imgaug4charon(path2labeledData,'png','xml',path2augmentedData)
ia4c.main(numofAugClones,maxImageSize)


########################
# Create training data #
########################

t = training_utils.trainDataCuration(nameOfTheNN,
                                    path2augmentedData,
                                    sourceImgType =imgExt)
t.chooseCandidateFiles()
t.renameLabelsVerbose() #or set dictionary
#t.labelChanger = {'TC.f W-': 'TC', 'Arena': 'arena', 'mark': 'marker', 'TC': 'TC', 'marker': 'marker', 'TC ': 'TC', 'TC.m W-': 'TC', 'TC.m W+': 'TC', 'TC.f W+': 'TC', 'arena': 'arena'}
t.labelChanger = {'arena_TL_autoBenzer': 'arena_TL_autoBenzer', 'abdomen': '!deleteThisLabel!', 'arena_TR_autoBenzer': 'arena_TR_autoBenzer', 'arena_TS_autoBenzer': 'arena_TS_autoBenzer', 'arena_LR_autoBenzer': 'arena_LR_autoBenzer', 'head': '!deleteThisLabel!','arena_LS_autoBenzer': 'arena_LS_autoBenzer', 'arena_LL_autoBenzer': 'arena_LL_autoBenzer', 'arena_TL_autoBenzer ': 'arena_TL_autoBenzer', 'fly': 'fly', 'arena_BR_autoBenzer': 'arena_LR_autoBenzer', 'arena_BL_autoBenzer': 'arena_LL_autoBenzer', 'arena_TSw_autoBenzer': 'arena_TS_autoBenzer'}


t.makeTrainDirs()
t.transfer_trainingData()

###################
# Run gen scripts #
# #################
reload(training_utils)
g = training_utils.runTrainingGenScripts(t,pythonPos='/home/bgeurten/anaconda3/envs/charon/bin/')
g.maxTrainSteps = 200000
g.run()


##########################
# Add more training data #
##########################

reload(training_utils)
t = training_utils.trainDataCuration('flyFinder_autoBenzer',
                                    '/home/bgeurten/ownCloud/trainData',
                                    sourceImgType ='png')
t.chooseCandidateFiles()
t.renameLabelsVerbose() #or set dictionary

t.transfer_AdditionalTrainingsData()

reload(training_utils)
g = training_utils.augmentTrainingGenScripts(t,[])
g.maxTrainSteps = 5000000
g.run()

