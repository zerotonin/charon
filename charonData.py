import datetime
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