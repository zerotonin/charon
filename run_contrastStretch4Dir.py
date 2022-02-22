from gettext import find
import contrastStretcher_8bit
import os 
from PIL import Image
from tqdm import tqdm
# This is a script to stretch the contrast of a directory of files, usually training sessions for cell data.
# Images from microscope cameras are usually badly set and not compatible with labelimg

def findFilesRec(folder,extension):
    return [os.path.join(dp, f) for dp, dn, filenames in os.walk(folder) for f in filenames if os.path.splitext(f)[1] == extension]

def main(folder,extension):
    imgPosList = findFilesRec(folder,extension)
    for imgPos in tqdm(imgPosList,desc='stretching images'):
        img = Image.open(imgPos)
        stretcher = contrastStretcher_8bit.contrastStretcher_8bit(img,mode='auto')
        imgStretched = stretcher.main()
        savePos = imgPos.split('.')[0]
        imgStretched.save(savePos+'.png','PNG')


main('/media/dataSSD/training','.tif')