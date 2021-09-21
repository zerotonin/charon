import os,shutil,glob,charon,datetime,time, pickle,gc
import charon, charonData
from pathlib import Path


class folderAutomaton:
    """ The folderAutomaton class observes a folder and its subfolder for new zip files, which will
        be analysed using the CHARON.

        These zip-files usually hold multiple experiments, documented in tif format. Dependent on
        the subfolder observed a distinct AI of the charon family is used to classify the cells in
        the zip-file. The resulting data files will be saved in the download tree of the same 
        parent directory. Example:


        parent Directory
            |___uploads
            |       |___locustNeuron <- empty 
            |       |___drosoNucleus 
            |       |       |__________experiment.zip <- will be analysed by drosoCellCounting AI
            |       |___triboleumNeuron
            |               |__________experiment.zip <- will be analysed by triboliumNeuron AI
            |___downloads
                    |___locustNeuron 
                    |___drosoNucleus <- this where the results of  drosoCellCounting AI get saved
                    |___triboleumNeuron <- this where the results of  triboliumNeuron AI get saved

    """    
    def __init__(self):
        """ This function initialsises the object and holds all nescessary paths to run charon. 

            Attention
            ---------
            On different systems all paths need to be adjusted to the correct position.
        """        
        #              tag : (INFERENCE_GRAPH_DIR, OUTPUT_DIR, INPUT_DIR)
        self.sharePath = '/media/dataSSD/ownCloudDrosoVis'
        self.inferencePath = os.path.join(self.sharePath,'inferenceGraphs')
        self.uploadPath    = os.path.join(self.sharePath,'cellDetector_charon/upload')
        self.downloadPath  = os.path.join(self.sharePath,'cellDetector_charon/download')
        self.cellTotalFile = os.path.join(self.inferencePath,'totalCount.csv')
        self.AIdict= {'locustNeuron'   :(os.path.join(self.inferencePath,'locustNeuron'        ),os.path.join(self.downloadPath,'locustNeuron'       ),os.path.join(self.uploadPath,'locustNeuron')),
                      'locustHaemo'    :(os.path.join(self.inferencePath,'locustHaemoInference'),os.path.join(self.downloadPath,'locustNeuronHaemo'  ),os.path.join(self.uploadPath,'locustNeuronHaemo')),
                      'flyBehav'       :(os.path.join(self.inferencePath,'flyBehav'            ),os.path.join(self.downloadPath,'flyBehav'           ),os.path.join(self.uploadPath,'flyBehav')),
                      'mosquitoDetector'   :(os.path.join(self.inferencePath,'mosquitoDetector'),os.path.join(self.downloadPath,'mosquitoDetector'   ),os.path.join(self.uploadPath,'mosquitoDetector')),
                      'drosoNucleus'   :(os.path.join(self.inferencePath,'drosoCellCounting'   ),os.path.join(self.downloadPath,'drosoNucleusCounter'),os.path.join(self.uploadPath,'drosoNucleusCounter')),
                      'triboliumNeuron':(os.path.join(self.inferencePath,'triboliumNeuron'     ),os.path.join(self.downloadPath,'triboliumNeuron'    ),os.path.join(self.uploadPath,'triboliumNeuron'))}
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
                        self.dataObjList.append(charonData.charonData(path,os.path.getsize(path),AItag))
    
    def analyseZips(self):
        """This function analyses a zip file completly, including transcoding, AI recognition, and output saving
        """        
        for dataObj in self.dataObjList:
            if dataObj.sizeConsistentFlag == True and dataObj.analyseFlag == False:
                dataObj.analyseFlag = True
                try:
                    x = charon.charon(dataObj.AItag)
                    x.runExperimentAnalysis(dataObj.fPos,protocolFlag=True)
                    dataObj.writeOutputFlag = True
                    dataObj.expirationDate  = datetime.datetime.now()+datetime.timedelta(days=4)    
                    dataObj.success         = True
                    dataObj.resultPos       = x.resultZipPos
                    self.writeImageCount(dataObj.AItag,dataObj.imageCounter)
                    del x
                except:
                    dataObj.success         = False
                    self.writeNegativeOutput(dataObj)

    def writeImageCount(self,AItag,cellNo):
        """This function records the number of analysed cell in the cell counter.

        In the file specified in self.cellTotalFile all recordings will be saved 

        Args:
            AItag ([type]): [description]
            cellNo ([type]): [description]
        """        

        if os.path.exists(self.cellTotalFile):
            cellTotalFile = open(self.cellTotalFile,'a')  # append if already exists 
        else:
            cellTotalFile = open(self.cellTotalFile,'w')   # make a new file if not 
            cellTotalFile.write("Date Time, AI Tag, Cell Number\n")


        cellTotalFile.write(datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")+ f",{AItag},{cellNo}\n")
        cellTotalFile.close()


    def writeNegativeOutput(self,dataObj):
        filename = os.path.join(self.AIdict[dataObj.AItag][1],'errors.txt')

        if os.path.exists(filename):
            append_write = 'a' # append if already exists
        else:
            append_write = 'w' # make a new file if not

        errorFile = open(filename,append_write)
        errorFile.write(datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")+" : Could not analyse " + str(dataObj.fPos) + '\n')
        errorFile.close()

    def clearObjectList(self):
        delMeList = list()
        for c in range(len(self.dataObjList)):
            if self.dataObjList[c].success == True:
                delMeList.append(c)

        for deletedIndex in delMeList:
            del self.dataObjList[deletedIndex]

    def delteExpiredOutputs(self):
        now               = datetime.datetime.now()
        nowInSeconds      = now.timestamp()
        fiveDaysInSeconds = 5*24*60*60      

        for root, dirs, files in os.walk(self.uploadPath):
            for file in files:
                if(file.endswith(".zip")):
                    fPos = os.path.join(root,file)
                    fileAgeInSeconds = os.path.getmtime(fPos)
                    if fileAgeInSeconds-nowInSeconds > fiveDaysInSeconds:
                        os.remove(fPos)



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


    def startUpCharon(self,loadCharonFlag):

        if loadCharonFlag == 'verbose':
            self.startUpDlg()
        elif loadCharonFlag == 'load':
            try:
                self.loadCharonObjList()
                print('Charon object list loaded! \n Only in death duty ends!\n\n')
            except:
                print('Charon object list NOT loaded! Starting fresh! \n Only in death duty ends!\n\n')
        elif loadCharonFlag == 'fresh':
            #self.startUpDlg()
            print('Starting fresh!\n Only in death duty ends!\n\n')

        
    def run(self,loadCharonFlag = 'load'):
        self.startUpCharon(loadCharonFlag)
        c=0
        while True:
            if c==1000:
                self.saveCharonObjList()
                os.system("find "+str(self.downloadPath)+"/* -mindepth 1 -mtime +5 -delete")
                c = 0
            self.checkFolders4NewObjects()
            self.analyseZips()
            
            c+=1
            gc.collect()
            time.sleep(5) 

if __name__ == "__main__":
    automaton = folderAutomaton()   
    automaton.run('fresh')             

