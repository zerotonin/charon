import os, shutil,glob,charon,datetime,time, pickle
from pathlib import Path


class charonData:
    def __init__(self,fPos,size,AItag):
        self.fPos               = fPos
        self.size               = size
        self.AItag              = AItag
        self.expirationDate     = 0
        self.newFlag            = True
        self.sizeConsistentFlag = False
        self.analyseFlag        = False
        self.success            = False
        self.resultPos          = ''

class folderAutomaton:
    def __init__(self):
        #              tag : (INFERENCE_GRAPH_DIR, OUTPUT_DIR, INPUT_DIR)
        self.AIdict= {'locustNeuron'   :('/media/dataSSD/ownCloudDrosoVis/inferenceGraphs/locustNeuron','/media/dataSSD/ownCloudDrosoVis/cellDetector_charon/download/locustNeuron','/media/dataSSD/ownCloudDrosoVis/cellDetector_charon/upload/locustNeuron'),
                      'locustHaemo'    :('/media/dataSSD/ownCloudDrosoVis/inferenceGraphs/locustHaemoInference','/media/dataSSD/ownCloudDrosoVis/cellDetector_charon/download/locustNeuronHaemo','/media/dataSSD/ownCloudDrosoVis/cellDetector_charon/upload/locustNeuronHaemo'),
                      'flyBehav'       :('/media/dataSSD/ownCloudDrosoVis/inferenceGraphs/flyBehav','/media/dataSSD/ownCloudDrosoVis/cellDetector/download/flyBehav','/media/dataSSD/ownCloudDrosoVis/cellDetector/upload/flyBehav'),
                      'triboliumNeuron':('/media/dataSSD/ownCloudDrosoVis/inferenceGraphs/triboliumNeuron', '/media/dataSSD/ownCloudDrosoVis/cellDetector/download/triboliumNeuron','/media/dataSSD/ownCloudDrosoVis/cellDetector/upload/triboliumNeuron')}
        self.dataObjListFpos = '/media/dataSSD/ownCloudDrosoVis/inferenceGraphs/charonObjList.dat'
        self.dataObjList     = list()

    def checkFolders4NewObjects(self):
        for AItag, AIpaths in self.AIdict.items():
            for path in Path(AIpaths[2]).rglob('*.zip'):    
                # check if there is already a data object with this file position
                newObj= True
                for dataObj in self.dataObjList:                  
                    # This is true if the object was already found 
                    if dataObj.fPos == path:
                       newObj = False                  # obviously it is not a new object
                       # now check if data consistency is given, 
                       # if the file is not dowloading anymore
                       if os.path.getsize(path) != dataObj.size:
                           dataObj.size = os.path.getsize(path)
                           dataObj.sizeConsistentFlag = False
                       else:
                           dataObj.sizeConsistentFlag = True
                # if after checking all previous data objects newObj is still true we have 
                # to add it to the list
                if newObj:

                    self.dataObjList.append(charonData(path,os.path.getsize(path),AItag))
    
    def analyseZips(self):
        for dataObj in self.dataObjList:
            if dataObj.sizeConsistentFlag == True and dataObj.analyseFlag == False:
                dataObj.analyseFlag = True
                try:
                    x = charon.charon(dataObj.AItag)
                    x.runExperimentAnalysis(dataObj.fPos)
                    dataObj.writeOutputFlag = True
                    dataObj.expirationDate  = datetime.datetime.now()+datetime.timedelta(days=4)    
                    dataObj.success         = True
                    dataObj.resultPos       = x.resultZipPos
                except:
                    dataObj.success         = False
                    self.writeNegativeOutput()


    def writeNegativeOutput(self,AItag):
        filename = os.path.join(self.AIdict[AItag][1],'errors.txt')

        if os.path.exists(filename):
            append_write = 'a' # append if already exists
        else:
            append_write = 'w' # make a new file if not

        errorFile = open(filename,append_write)
        errorFile.write(datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")+" : Could not analyse " + dataObj.fPos + '\n')
        errorFile.close()



    def delteExpiredOutputs(self):
        now = datetime.datetime.now()
        c = 0
        delMeList = list()
        for dataObj in self.dataObjList:
            elapsedTime = dataObj.expirationDate -now
            if elapsedTime.total_seconds() < 0:
                try:
                    os.remove(dataObj.resultPos)
                except:
                    print(dataObj.resultPos ' was allready deleted')
                delMeList.append(c)
        
        for deletedIndex in delMeList:
            del self.dataObjList[deletedIndex]
                

    def pingAnswer(self):
        pass
    
    def loadCharonObjList(self):       
        try:
            with open(self.dataObjListFpos) as f:
                objList = pickle.load(f)
        except:
           objList = []

        self.dataObjList = objList

    def saveCharonObjList(self):
        with open(self.dataObjListFpos, "wb") as f:
            pickle.dump(self.dataObjList, f)

        

    def run(self):
        c=0
        while True:
            if c==1000:
                self.saveCharonObjList()
                c = 0

            self.checkFolders4NewObjects()
            for dataObj in self.dataObjList:
                print(dataObj.fPos,dataObj.sizeConsistentFlag)
            print('===========================================')
            self.analyseZips()
            c+=1
            time.sleep(5) 

                

