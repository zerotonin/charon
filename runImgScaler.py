
import imageScaler
from importlib import reload
reload(imageScaler)
pDir ='/media/dataSSD/multipliedData/trainData_penguin2'
x = imageScaler.imageScaler(pDir,1024)
x.resizeFolder()