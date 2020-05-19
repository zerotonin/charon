from importlib import reload
import charon, time,  training_utils
#standard zipped experiment
reload(charon)
x = charon.charon('locustHaemo')
x.OUTPUT_DIR='/media/gwdg-backup/BackUp/Debbie/analysed'
start = time.time()
x.runExperimentAnalysis("/media/gwdg-backup/BackUp/Debbie/cellAna_new/2019-11-25_Hemocytes-60°C#1.zip")
end = time.time()
print(end - start)
start = time.time()
x.runExperimentAnalysis("/media/gwdg-backup/BackUp/Debbie/cellAna_new/2020-03-12_dHl-hemocytes#4.zip")
end = time.time()
print(end - start)

reload(training_utils)