import os,shutil,glob,charon,datetime,time, pickle,gc
from pathlib import Path

class charonData:
    def __init__(self,fPos,size,AItag):
        self.fPos               = fPos
        self.size               = size
        self.AItag              = AItag
        self.expirationDate     = datetime.datetime.now()+datetime.timedelta(days=4)    
        self.newFlag            = True
        self.sizeConsistentFlag = False
        self.analyseFlag        = False
        self.success            = False
        self.resultPos          = ''

class folderAutomaton:
    def __init__(self):
        #              tag : (INFERENCE_GRAPH_DIR, OUTPUT_DIR, INPUT_DIR)
        self.sharePath = '/media/dataSSD/ownCloudDrosoVis'
        self.inferencePath = os.path.join(self.sharePath,'inferenceGraphs')
        self.uploadPath    = os.path.join(self.sharePath,'cellDetector_charon/upload')
        self.downloadPath  = os.path.join(self.sharePath,'cellDetector_charon/download')
        self.AIdict= {'locustNeuron'   :(os.path.join(self.inferencePath,'locustNeuron'        ),os.path.join(self.downloadPath,'locustNeuron'     ),os.path.join(self.uploadPath,'locustNeuron')),
                      'locustHaemo'    :(os.path.join(self.inferencePath,'locustHaemoInference'),os.path.join(self.downloadPath,'locustNeuronHaemo'),os.path.join(self.uploadPath,'locustNeuronHaemo')),
                      'flyBehav'       :(os.path.join(self.inferencePath,'flyBehav'            ),os.path.join(self.downloadPath,'flyBehav'         ),os.path.join(self.uploadPath,'flyBehav')),
                      'triboliumNeuron':(os.path.join(self.inferencePath,'triboliumNeuron'     ),os.path.join(self.downloadPath,'triboliumNeuron'  ),os.path.join(self.uploadPath,'triboliumNeuron'))}
        self.dataObjListFpos = os.path.join(self.inferencePath,'charonObjList.dat')
        self.dataObjList     = list()

    def checkFolders4NewObjects(self):
        for AItag, AIpaths in self.AIdict.items():
            #print(AIpaths[2])
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
                    if path.name == 'ping.zip':
                        self.pingAnswer(path)
                    else:
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
            elapsedTime = dataObj.expirationDate - now
            if elapsedTime.total_seconds() < 0:
                try:
                    os.remove(dataObj.resultPos)
                except:
                    #print(dataObj.resultPos, ' was allready deleted')
                    delMeList.append(c)
        
        for deletedIndex in delMeList:
            del self.dataObjList[deletedIndex]
                

    def pingAnswer(self,path):
        #print('saw a ping @ ', path)
        shutil.move(path,os.path.join(os.path.join(self.downloadPath,path.parent.name),'pong.zip'))
    
    def loadCharonObjList(self):       
        try:
            with open(self.dataObjListFpos,'rb') as f:
                objList = pickle.load(f)
        except:
           objList = []

        self.dataObjList = objList

    def saveCharonObjList(self):
        with open(self.dataObjListFpos, "wb") as f:
            pickle.dump(self.dataObjList, f)

    def startUpDlg(self,answer='u'):
        if answer != 'y' and answer != 'n':
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

