from importlib import reload
import charon,cv2
from pathlib import Path
import pandas as pd
from tqdm import tqdm
# do everything by hand
reload(charon)

x = charon.charon("funnelFinder")
fileList = list()
data = list()
for path in Path('/media/gwdg-backup/BackUp/Paul_Funnel').rglob('*.JPG'):
    fileList.append(str(path))

for fPos in tqdm(fileList,desc='analysing images'):
    image = cv2.imread(fPos)
    boxes,scores,classes = x.generalMultiClassDetection(image)  

    detIndex  = list(range(len(boxes)))
    fileIndex =[fPos for x in detIndex]
    data+= list(zip(fileIndex,detIndex,boxes,scores,classes))