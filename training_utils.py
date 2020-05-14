import os
from tqdm import tqdm
import xml.etree.ElementTree as ET
from PIL import Image


class training_utils:
    def __init__(self,WORK_DIR='/media/dataSSD/trainingData/haemoTrain'):

        self.WORK_DIR    = WORK_DIR
        self.TEST_DIR    = '/media/dataSSD/trainingData/Cell/test'
        self.TRAIN_DIR   = '/media/dataSSD/trainingData/Cell/train'

    
    def getLabelsFromXML(self, file):
        nameList = list()
        root = ET.parse(file).getroot()
        for nameText in root.iter('name'):
            nameList.append(nameText.text)
        return set(nameList)
    
    def getFilePos_search(self,path,ext):
        
        fList = []
        # r=root, d=directories, f = files
        for r, d, f in os.walk(path):
            for file in f:
                if ext in file:
                    fList.append(os.path.join(r, file))
        fList.sort()
        return fList

    def getFileCandidates(self):

        xmlList = self.getFilePos_search(self.WORK_DIR,'xml')
        imgList = self.getFilePos_search(self.WORK_DIR,'tif')
        self.sourceData = (xmlList,imgList)
    
    def shortenCandidatesByName(self):

        xmlList = self.sourceData[0]
        imgList = self.sourceData[1]
        xmlPath = []
        imgPath = []
        for path in xmlList:
            xmlPath.append(os.path.splitext(path)[0])
        for path in imgList:
            imgPath.append(os.path.splitext(path)[0]) 
        
        self.candidates = list(set(imgPath) & set(xmlPath))
        self.candidates.sort()
    
    def analyseCandidateObjects(self):
        delMeList = []
        labelsAll = set()
        for i in range(len(self.candidates)):
            xmlFile = self.candidates[i]+'.xml'
            labels = self.getLabelsFromXML(xmlFile)
            if len(labels) == 0:
                delMeList.append(i)
            else:
                labelsAll = labelsAll | labels
        self.labelsAll = labelsAll
        return delMeList

    def renameLabelsVerbose(self):
        print('These labels were entered:')
        print('==========================')
        for i, dest in enumerate(self.labelsAll, 1):
            print(" %d. %s" % (i, dest))
        print('')
        correct = '?'
        while (correct != 'y') and (correct != 'n'):
            correct = input('Is this correct? [y/n]')

        self.labelChanger = dict()
        if correct == 'y':
            print('All labels will be used!')
            for label in self.labelsAll:
                self.labelChanger[label] = label
        else:
            for label in self.labelsAll:

                print('============================================')
                self.enterNewLabel(label)

        print('============================================')
        print('Here are the rules for relabling:')
        print(self.labelChanger)
        
    
    def enterNewLabel(self,label):

        print("Old label: " + label)
        correct = '?'
        while (correct != 'y') and (correct != 'n'):
            correct = input('Do you want to change the label? [y/n]')

        if correct == 'n':

            self.labelChanger[label] = label

        else:
            correct = '?'
            while (correct != 'y'):
                newLabel = input('Enter new label: ')
                print(label + " -> " + newLabel)
                correct = input('Is this correct? [y/n]')
            self.labelChanger[label] = newLabel
    
    def chooseCandidateFiles(self):
        # get file Names
        self.getFileCandidates()
        # sort out those that have no xml or img partner
        self.shortenCandidatesByName()
        # get empty candidates in delMeList
        # get all used labels in self.labelsAll
        delMeList = self.analyseCandidateObjects()
        # delete empty candidates
        for index in sorted(delMeList, reverse=True):
            del self.candidates[index]
    

    def transfer_trainingData(self):
        # initialize counter
        testCounter  = 0
        trainCounter = 0
        fileI = 0
        #run through all files
        for cand in tqdm(self.candidates,desc='transfering'):
            # get the candidate
            
            # source and traget filenames
            imgSourcePos = cand+'.tif'
            xmlSourcePos = cand+'.xml'

            # 20% of the training data goes to testing
            if fileI%5 == 0:
                #this file goes to testing
                imgTargetPos =os.path.join(self.TEST_DIR,'Image_' + str(testCounter).zfill(4) + '.png')
                xmlTargetPos =os.path.join(self.TEST_DIR,'Image_' + str(testCounter).zfill(4) + '.xml')
                testCounter += 1
            else:
                #this file goes to training
                imgTargetPos =os.path.join(self.TRAIN_DIR,'Image_' + str(trainCounter).zfill(4) + '.png')
                xmlTargetPos =os.path.join(self.TRAIN_DIR,'Image_' + str(trainCounter).zfill(4) + '.xml')
                trainCounter += 1

            
            imageName = os.path.basename(imgTargetPos)
            imgFolder = os.path.basename(os.path.dirname(imgTargetPos))
            fileI +=1

            #copy and transcode image
            im = Image.open(imgSourcePos)
            im.save(imgTargetPos)

            # copy xml file

            tree = ET.parse(xmlSourcePos)
            root = tree.getroot() 
            path = root.find('path')
            path.text = imgTargetPos
            folder = root.find('folder')
            folder.text = imgFolder
            filename = root.find('filename')
            filename.text = imageName
            for objAnno in root.findall('object'):
                name = objAnno.find('name')
                oldName = name.text
                name.text = self.labelChanger[oldName]
            tree.write(xmlTargetPos)

