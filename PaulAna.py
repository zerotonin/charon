from importlib import reload
import charon,cv2,charonPresenter
from pathlib import Path
import pandas as pd
from tqdm import tqdm
# do everything by hand
reload(charon)

x = charon.charon("funnelFinder")
fileList = list()
data = list()
srcDir = '/media/gwdg-backup/BackUp/Paul_Funnel'

for path in Path(srcDir).rglob('*.JPG'):
    fileList.append(str(path))

for fPos in tqdm(fileList,desc='analysing images'):
    image = cv2.imread(fPos)
    boxes,scores,classes = x.generalMultiClassDetection(image)  

    detIndex  = list(range(len(boxes)))
    fileIndex =[fPos for x in detIndex]
    data+= list(zip(fileIndex,detIndex,boxes,scores,classes))

indices = [[x[0] for x in data ],[x[1] for x in data ]]
rawData = [(x[4],x[3],x[2][0],x[2][1],x[2][2],x[2][3]) for x in data]
columns    = ['label','quality','y_min','x_min','y_max','x_max']
# index 
df = pd.DataFrame(rawData, index=indices,columns = columns)
df.to_hdf('./resultDataFrame.h5',key='df')


fPos = '/media/gwdg-backup/BackUp/Paul_Funnel/run 1/2020_05_22__16__tm6bpzl__3_ortho_BH.JPG'
fPos = fileList[156]
df.loc[[fPos]]
cP = charonPresenter.charonPresenter(fPos,'','image')
cP.frameNo = fPos
cP.df = df
cP.detFileLoaded = True
cP.imageScaling = 0.25
frame = cP.main(0, True)
cv2.imwrite('./example.png',frame)