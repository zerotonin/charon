import os, shutil,glob
from pathlib import Path


class charonData:
    def __init__(self,fPos,size,AItag):
        self.fPos               = fPos
        self.size               = size
        self.AItag              = AItag
        self.expirationDate     = 0
        self.newFlag            = True
        self.analysedFlag       = False
        self.sizeConsistentFlag = False
        self.writeOutputFlag    = False
        self.deleteOutputFlag   = False

class folderAutomaton:
    def __init__(self):
        #              tag : (INFERENCE_GRAPH_DIR, OUTPUT_DIR, INPUT_DIR)
        self.AIdict= {'locustNeuron'   :('/media/dataSSD/ownCloudDrosoVis/inferenceGraphs/locustNeuron','/media/dataSSD/ownCloudDrosoVis/cellDetector_charon/download/locustNeuron','/media/dataSSD/ownCloudDrosoVis/cellDetector_charon/upload/locustNeuron'),
                      'locustHaemo'    :('/media/dataSSD/ownCloudDrosoVis/inferenceGraphs/locustHaemoInference','/media/dataSSD/ownCloudDrosoVis/cellDetector_charon/download/locustNeuronHaemo','/media/dataSSD/ownCloudDrosoVis/cellDetector_charon/upload/locustNeuronHaemo'),
                      'flyBehav'       :('/media/dataSSD/ownCloudDrosoVis/inferenceGraphs/flyBehav','/media/dataSSD/ownCloudDrosoVis/cellDetector/download/flyBehav','/media/dataSSD/ownCloudDrosoVis/cellDetector/upload/flyBehav'),
                      'triboliumNeuron':('/media/dataSSD/ownCloudDrosoVis/inferenceGraphs/triboliumNeuron', '/media/dataSSD/ownCloudDrosoVis/cellDetector/download/triboliumNeuron','/media/dataSSD/ownCloudDrosoVis/cellDetector/upload/triboliumNeuron')}

        self.dataObjList  = list()
        self.fileSchedule = list()

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
        pass
    
    def writeNegativeOutput(self):
        pass
    def delteExpiredOutouts(self):
        pass


                

