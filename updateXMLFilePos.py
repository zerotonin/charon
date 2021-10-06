import os,sys, getopt
import xml.etree.ElementTree as ET
from tqdm import tqdm

class updateXMLFilePos():

    def __init__(self,filePosition):
        self.filePath  = filePosition
        self.parentDir = os.path.dirname(self.filePath)
        self.folder    = os.path.basename(self.parentDir)


    def main(self):

            # copy and update xml file

            #read in file
            tree = ET.parse(self.filePath)
            # get start of file
            root = tree.getroot() 
            #update image subfolder
            folder = root.find('folder')
            folder.text = self.folder
            #update image path
            filename = root.find('filename')
            path = root.find('path')
            path.text = os.path.join(self.parentDir,filename.text)
            #write xml
            tree.write(self.filePath)



if __name__ == '__main__':
    
    # get input variables
    usageStr = 'usage: updateXMLFilePos.py -i <xmlFileDir>'
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hi:",["xmlDir="])
        print(sys.argv)
    except getopt.GetoptError:
        print(usageStr)
        sys.exit(2)

    #parse Inputs
    xmlDir       = False

    for o, a in opts:
        # if user asks for help 
        if o == '-h':
            print(usageStr)
            sys.exit(2)
        elif o == '-i':
            xmlDir = a

    if os.path.isdir(xmlDir) == False:
        raise ValueError(f'-i is not an existing file: {xmlDir} ')

    for xmlFilePos in tqdm(os.listdir(xmlDir),'parsing xml Files'):
        if xmlFilePos.endswith(".xml"):

            xmlObj = updateXMLFilePos(os.path.join(xmlDir,xmlFilePos))
            xmlObj.main()
