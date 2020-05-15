import os, generate_tfrecord,xml_to_csv
from tqdm import tqdm
import xml.etree.ElementTree as ET
from PIL import Image


class trainDataCuration:
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

            fileI +=1
            # GET parent folder name and filename separately for xml update
            imageName = os.path.basename(imgTargetPos)
            imgFolder = os.path.basename(os.path.dirname(imgTargetPos))
         

            # copy and update xml file

            #read in file
            tree = ET.parse(xmlSourcePos)
            # get start of file
            root = tree.getroot() 
            #update image position values
            path = root.find('path')
            path.text = imgTargetPos
            folder = root.find('folder')
            folder.text = imgFolder
            filename = root.find('filename')
            filename.text = imageName
            # now update the object labels/names
            for objAnno in root.findall('object'): # find all objects
                # get the name field
                name = objAnno.find('name')
                # extract former name field content as key value for the label changer dict
                oldName = name.text
                #update with new label from labelChanger dict
                name.text = self.labelChanger[oldName]
            #write the updated xml values to target position
            tree.write(xmlTargetPos)

            #copy and transcode image
            im = Image.open(imgSourcePos)
            #save image as png
            im.save(imgTargetPos)

class runTrainingGenScripts:
    def __init__(self,
                 train_csv_file = '/media/dataSSD/trainingData/Cell/train_labels.csv',
                 train_img_path = '/media/dataSSD/trainingData/Cell/train',
                 test_csv_file  = '/media/dataSSD/trainingData/Cell/test_labels.csv',
                 test_img_path  = '/media/dataSSD/trainingData/Cell/test',
                 output_path    = '/media/dataSSD/trainingData/Cell/'):
        self.train_csv_file = train_csv_file
        self.train_img_path = train_img_path
        self.test_csv_file  = test_csv_file
        self.test_img_path  = test_img_path
        self.output_path    = output_path
    
    def warn(self):
        print("-------------------------------------------------------------------")
        print("| Before you can run this function and create the training files, |")
        print("| you have to CHANGE the FUNCTION class_text_to_int in the FILE   |")
        print("| generate_tfrecord.py !                                          |")
        print("-------------------------------------------------------------------")
        print(" ")
        
        correct = input('Did you do so? [y/n]')
        while (correct != 'y') and (correct != 'n'):
            print('Did not recognise answer')
            correct = input('Did you do so? [y/n]')

        if correct == 'n':
            return False
        else:
            return True

    def run(self):

        if self.warn():

            xml_to_csv.main(self.test_img_path,self.test_csv_file)
            xml_to_csv.main(self.train_img_path,self.train_csv_file)
            generate_tfrecord.main(os.path.join(self.output_path + "test.record"),self.test_img_path,self.test_csv_file)
            generate_tfrecord.main(os.path.join(self.output_path + "train.record"),self.train_img_path,self.train_csv_file)
  
class makelabelMapFile:
    def __init__(self,names = [], ids = []):
        self.names = names
        self.ids  = ids
        self.outputPath = '/media/dataSSD/trainingData/Cell/'
        self.outputFile = 'labelmap.pbtxt'
    
    def printNameIDs(self):
        if self.checkNameID():
            for x,y in zip(self.ids,self.names):
                print(x,y)
        

    def checkNameID(self):
        if len(self.ids) == 0 or len(self.names) == 0:
            print("IDs or names are empty!")
            return False
        if len(self.ids) != len(self.names):
            print("IDs and names have different lengths")
            return False
        return True
    
    def answerCorrectDlg(self,answer):

        correct =input ('You entered ' + answer + '. Is this correct?  [y/n]')
        while (correct != 'y') and (correct != 'n'):
            print('Did not recognise answer')
            correct =input ('You entered ' + answer + '. Is this correct?  [y/n]')
        
        if correct =='y':
            return True
        else:
            return False

    def getLabelsVerbose(self):

        self.names = []
        self.ids   = []
        moreLabelsAns = input('Do you want to add another label, if you answer y old labels are deleted [y/n]')
        while (moreLabelsAns != 'y') and (moreLabelsAns != 'n'):
            print('Did not recognise answer')
            moreLabelsAns = input('Do you want to add another label? [y/n]')
        
        while (moreLabelsAns == 'y'):

            print('===================================================================')
            labelName = input('Enter label name:')
            labelCorrect = self.answerCorrectDlg(labelName)
            while labelCorrect == False:
                labelName = input('Enter label name:')  
                labelCorrect = self.answerCorrectDlg(labelName)
            
            self.names.append(labelName)
    
            idNum = input('Enter id number:')
            idCorrect = self.answerCorrectDlg(idNum)
            while idCorrect == False:
                idNum = input('Enter id number:')
                idCorrect = self.answerCorrectDlg(idNum)
            
            self.ids.append(idNum)


            moreLabelsAns = input('Do you want to add another label, if you answer y old labels are deleted [y/n]')
            while (moreLabelsAns != 'y') and (moreLabelsAns != 'n'):
                print('Did not recognise answer')
                moreLabelsAns = input('Do you want to add another label? [y/n]')
        
    def writeFile(self):
        if self.checkNameID:
            outF = open(os.path.join(self.outputPath,self.outputFile), "w")
            for idNum,nameStr in zip(self.ids,self.names):
              # write line to output file
              outF.write("\n")
              outF.write("item {\n")
              outF.write("  id: " + str(idNum) +"\n")
              outF.write("  name: '" + nameStr +"'\n")
              outF.write("}\n")
            outF.close()
            print('File writen at ' + os.path.join(self.outputPath,self.outputFile))


class adaptTFconfigFile:
    def __init__(self,tag='cells',labels= ['alive','dead']):
        self.originalConfigFile = '/home/bgeurten/tensorFlowModels/research/object_detection/samples/configs/faster_rcnn_inception_v2_pets.config'
        self.targetConfigFile = '/media/dataSSD/trainingData/Cell/faster_rcnn_inception_v2_' + tag + '.config'
        self.labels = labels
        self.tag = tag

    def readConfig(self):
        with open(self.originalConfigFile, 'r') as file:
            # read a list of lines into data
            config = file.readlines()
        self.config = config
    
    def updateLabelNum(self):

        self.config[8] = '    num_classes: '+ str(len(self.labels)) +'\n'

    
