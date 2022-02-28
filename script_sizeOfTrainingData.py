 import pandas as pd
 
 fPos = '/home/bgeurten/Downloads/train_labels.csv'
 fPos2 = '/home/bgeurten/Downloads/train_labels.csv'
 df = pd.read_csv(fPos)
 df2 =  pd.read_csv(fPos2)
 df = pd.concat((df,df2))

 print(f'DataSet includes {len(df)} cells in {len(df.filename.unique())} images' )