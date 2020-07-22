import os,shutil,glob,charon,datetime,time, pickle,gc
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
        self.AIdict= {'locustNeuron'   :('/media/dataSSD/ownCloudDrosoVis/inferenceGraphs/locustNeuron'        ,'/media/dataSSD/ownCloudDrosoVis/cellDetector_charon/download/locustNeuron'     ,'/media/dataSSD/ownCloudDrosoVis/cellDetector_charon/upload/locustNeuron'),
                      'locustHaemo'    :('/media/dataSSD/ownCloudDrosoVis/inferenceGraphs/locustHaemoInference','/media/dataSSD/ownCloudDrosoVis/cellDetector_charon/download/locustNeuronHaemo','/media/dataSSD/ownCloudDrosoVis/cellDetector_charon/upload/locustNeuronHaemo'),
                      'flyBehav'       :('/media/dataSSD/ownCloudDrosoVis/inferenceGraphs/flyBehav'            ,'/media/dataSSD/ownCloudDrosoVis/cellDetector_charon/download/flyBehav'         ,'/media/dataSSD/ownCloudDrosoVis/cellDetector_charon/upload/flyBehav'),
                      'triboliumNeuron':('/media/dataSSD/ownCloudDrosoVis/inferenceGraphs/triboliumNeuron'     ,'/media/dataSSD/ownCloudDrosoVis/cellDetector_charon/download/triboliumNeuron'  ,'/media/dataSSD/ownCloudDrosoVis/cellDetector_charon/upload/triboliumNeuron')}
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
                    print(path)
                    if path.name == 'ping.zip':
                        self.pingAnswer(path)
                        print('saw the ping')
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
                    del x
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
                    print(dataObj.resultPos, ' was allready deleted')
                delMeList.append(c)
        
        for deletedIndex in delMeList:
            del self.dataObjList[deletedIndex]
                

    def pingAnswer(self,path):
        shutil.move(path,os.path.join(os.path.join('/media/dataSSD/ownCloudDrosoVis/cellDetector/download',path.parent.name),'pong.zip'))
    
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

    def startUpDlg(self):

        answer = input('Do I need to load old charon objects? [y/n]: ')
        while answer != 'y' and answer != 'n':
            answer = input('Do I need to load old charon objects? [y/n]: ')
        

        if answer == 'y':
            try:
                self.loadCharonObjList()
                print('Charon object list loaded!')
            except:
                print('Charon object list NOT loaded! Starting fresh!')
        else:
            print('Starting fresh!')
        
        print('Only in death duty ends!')

    def run(self):
        self.startUpDlg()
        c=0
        while True:
            if c==1000:
                self.saveCharonObjList()
                c = 0
            self.checkFolders4NewObjects()
            self.analyseZips()
            self.delteExpiredOutputs()
            c+=1
            gc.collect()
            time.sleep(5) 


if __name__ == "__main__":
    automaton = folderAutomaton()   
    automaton.run()             

