from importlib import reload
import charon, time,  training_utils

reload(training_utils)

t = training_utils.trainDataCuration('flyFinder',
                                    '/media/gwdg-backup/labelData4DrosoFinder',
                                    sourceImgType ='png')
t.chooseCandidateFiles()
t.renameLabelsVerbose() #or set dictionary
#t.labelChanger = {'male1': 'male 1', 'agression': 'aggression', 'male 2': 'male 2', 'male 1': 'male 1', 'homo courtship': 'homo courtship', 'male2': 'male 2', 'courtship': 'courtship', 'female': 'female'}
#t.labelChanger = {'arena-TR_manuBenzer': 'arena_TR_manuBenzer', 'arena_TL_manuBenzer': 'arena_TL_manuBenzer', 'arene_LR_manuBenzer': 'arena_LR_manuBenzer', 'arena-LR_manuBenzer': 'arena_LR_manuBenzer', 'fly': 'fly', 'arena_LR_manuBenzer': 'arena_LR_manuBenzer', 'adomen': 'abdomen', 'abdomen': 'abdomen', 'head': 'head', 'arena_LL_autoBenzer': 'arena_LL_autoBenzer', 'arena_RL_manuBenzer': 'arena_LR_manuBenzer', 'arena_TR_autoBenzer': 'arena_TR_autoBenzer', 'arena_LLw_manuBenzer': 'arena_LL_manuBenzer', 'arene_TR_manuBenzer': 'arena_TR_manuBenzer', 'arena_food_tc': 'arena_food_tc', 'arena_LS_autoBenzer': 'arena_LS_autoBenzer', 'arene_LL_manuBenzer': 'arena_LL_manuBenzer', 'arene_TL_manuBenzer': 'arena_TL_manuBenzer', 'arena-LL_manuBenzer': 'arena_LL_manuBenzer', 'arena_TwL_manuBenzer': 'arena_TL_manuBenzer', 'arena_TL_autoBenzer': 'arena_TL_autoBenzer', 'andomen': 'abdomen', 'arena_TS_autoBenzer': 'arena_TS_autoBenzer', 'arena_TR_manuBenzer': 'arena_TR_manuBenzer', 'arena_LL_manuBenzer': 'arena_LL_manuBenzer', 'arena_LR_autoBenzer': 'arena_LR_autoBenzer', 'arena_LwR_manuBenzer': 'arena_LR_manuBenzer'}

t.makeTrainDirs()
t.transfer_trainingData()


reload(training_utils)
g = training_utils.runTrainingGenScripts(t)
g.run()


##########################
# Add more training data #
##########################

reload(training_utils)
t = training_utils.trainDataCuration('flyFinder',
                                    '/media/dataSSD/trainingData/topFly/train',
                                    sourceImgType ='png')
t.chooseCandidateFiles()
t.renameLabelsVerbose() #or set dictionary
