from importlib import reload
import charon, time,  training_utils, imageMultiplier, imageScaler



reload(training_utils)
path2labeledData = '/media/dataSSD/multipliedData/trainData_penguin2'
nameOfTheNN = 'penguinPicker4x'
imgExt = 'png'

##################################
# scale your labeled if to large #
##################################

iS = imageScaler.imageScaler(path2labeledData,1024,sourceImgType =imgExt,overWriteMode=False)
iS.scaleFolder()

###############################
# quadrupel your labeled data #
###############################
tm = imageMultiplier.imageMultiplier(path2labeledData,sourceImgType =imgExt,flipType='hvb')
tm.flipFolder()


########################
# Create training data #
########################

t = training_utils.trainDataCuration(nameOfTheNN,
                                    path2labeledData,
                                    sourceImgType =imgExt)
t.chooseCandidateFiles()
t.renameLabelsVerbose() #or set dictionary
#t.labelChanger = {'TC.f W-': 'TC', 'Arena': 'arena', 'mark': 'marker', 'TC': 'TC', 'marker': 'marker', 'TC ': 'TC', 'TC.m W-': 'TC', 'TC.m W+': 'TC', 'TC.f W+': 'TC', 'arena': 'arena'}
#t.labelChanger = {'arena_TL_autoBenzer': 'arena_TL_autoBenzer', 'arena_LR_autoBenzer': 'arena_LR_autoBenzer', 'arena_TR_autoBenzer': 'arena_TR_autoBenzer', 'head': 'head', 'arena_LL_autoBenzer': 'arena_LL_autoBenzer', 'fly': 'fly', 'arena_TL_autoBenzer ': 'arena_TL_autoBenzer', 'arena_TS_autoBenzer': 'arena_TS_autoBenzer', 'abdomen': 'abdomen', 'arena_LS_autoBenzer': 'arena_LS_autoBenzer'}
t.makeTrainDirs()
t.transfer_trainingData()

###################
# Run gen scripts #
# #################
reload(training_utils)
g = training_utils.runTrainingGenScripts(t,pythonPos='/home/bgeurten/anaconda3/envs/charon/bin/')
g.maxTrainSteps = 1000000
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

