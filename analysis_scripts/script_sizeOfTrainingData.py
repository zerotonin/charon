 import pandas as pd
 
 fPos = '/media/dataSSD/trainingData/triboliumNeuron2/test_labels.csv'
 fPos2 = '/media/dataSSD/trainingData/triboliumNeuron2/train_labels.csv'
 df = pd.read_csv(fPos)
 df2 =  pd.read_csv(fPos2)
 df = pd.concat((df,df2))

 print(f'DataSet includes {len(df)} cells in {len(df.filename.unique())} images' )