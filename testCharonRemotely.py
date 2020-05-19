from importlib import reload
import charon, time,  training_utils
#standard zipped experiment
reload(charon)
x.charon.charon('locustHaemo')
x.OUTPUT_DIR='/media/gwdg-backup/BackUp/Debbie/analysed'
start = time.time()
x.runExperimentAnalysis("/media/gwdg-backup/BackUp/Debbie/cellAna_new/2020-05-06_Lm-neuron-TRB#1.zip")
end = time.time()
print(end - start)
start = time.time()
x.runExperimentAnalysis("/media/gwdg-backup/BackUp/Debbie/cellAna_new/Neuron Test #1.zip")
end = time.time()
print(end - start)

reload(training_utils)