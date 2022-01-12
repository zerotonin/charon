import glob,os
class charonListManager:

    def __init__(self,sourceDir,imageExt,dataExt):
        self.sourceDir = sourceDir
        self.imageExt  = imageExt
        self.dataExt   = dataExt
        
        self.imgFileList = list()
        self.dataFileList = list()

    def getFilesInDir(self,ext):
        fileList = list()
        for index, file in enumerate(glob.glob(f'{self.sourceDir}{os.sep}*.{ext}')):
            fileList.append(file)
        fileList.sort()
        return fileList
    

    def cleanLists(self):
        # clean lists of non existant files exists
        self.dataFileList = self.keepOnlyExistingFiles(self.dataFileList)
        self.imgFileList = self.keepOnlyExistingFiles(self.imgFileList)

        # only keep those files that are  in both lists
        # combine both lists without extensions        
        combiList = [i.split('.')[0] for i in self.imgFileList] +[i.split('.')[0] for i in self.dataFileList]
        # get a list of the unique values
        combiListUnique = list(set(combiList))
        # now delte once each unique value of the combination list. 
        # All single values will disappear and only those that occure twice will be kept
        for entry in combiListUnique:
            combiList.remove(entry)
        # now we recreate both lists based on combilist
        self.imgFileList = [x+'.'+self.imageExt for x in combiList]
        self.dataFileList = [x+'.'+self.dataExt for x in combiList]

    def keepOnlyExistingFiles(self,testList):
        boolList       = [os.path.isfile(x) for x in testList]
        return [i for (i, v) in zip(testList, boolList) if v]

    def get_xml_img_filepairs(self):

        self.imgFileList = self.getFilesInDir(self.imageExt)
        self.dataFileList = self.getFilesInDir(self.dataExt)
        self.cleanLists()
        return self.imgFileList,self.dataFileList