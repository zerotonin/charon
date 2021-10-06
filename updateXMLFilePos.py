import os,sys, getopt
import xml.etree.ElementTree as ET

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
    usageStr = 'usage: updateXMLFilePos.py -i <xmlFilePos>'
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hi:",["xmlFilePos="])
        print(sys.argv)
    except getopt.GetoptError:
        print(usageStr)
        sys.exit(2)

    #parse Inputs
    xmlFilePos       = False

    for o, a in opts:
        # if user asks for help 
        if o == '-h':
            print(usageStr)
            sys.exit(2)
        elif o == '-i':
            xmlFilePos = a

    if os.path.isfile(xmlFilePos) == False:
        raise ValueError(f'-i is not an existing file: {xmlFilePos} ')


    xmlObj = updateXMLFilePos(xmlFilePos)
    xmlObj.main()
