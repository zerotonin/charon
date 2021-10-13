import pandas as pd
import analysePupaePosition
from tqdm import tqdm

class larvaePosAna():
    def __init__(self,dfPos):
        self.dfFilePos = dfPos 
        self.df = pd.read_hdf(self.dfFilePos,key='df')


    def getFunnelSet(self,dateStr,hourInt,strainStr):
        funnelSet = self.df[self.df['date'] == dateStr]
        return funnelSet.loc[(funnelSet['hour'] == hourInt) | (funnelSet['genType'] == strainStr)]

    def getViewSet(self,funnelSet,viewStr):
        return funnelSet[funnelSet['imgPosStr'] == viewStr]

    def getAnalysisSets(self,dateStr,hourInt,strainStr,viewStr):
        funnelSet = self.getFunnelSet(dateStr,hourInt,strainStr)
        viewSet   = self.getViewSet(funnelSet,viewStr)
        larvaeSet = viewSet.loc[(viewSet['label'] == 'inner_larva')|(viewSet['label'] == 'outter_larva')]
        funnel    = viewSet[viewSet['label'] == 'funnel']
        return (larvaeSet,funnel)

    def larvaeInFunnelNorm(self,anaSets):
        larvaeDF = anaSets[0].copy(deep =True)
        funnelDF = anaSets[1]
        for col in ['y_min', 'y_max']:
            larvaeDF[col] = larvaeDF[col]-funnelDF.iloc[0]['y_min']
        for col in ['x_min', 'x_max']:
            larvaeDF[col] = larvaeDF[col]-funnelDF.iloc[0]['x_min']
        return larvaeDF
    
    def larvaPosAna(self,dateStr,hourInt,strainStr,viewStr):
        anaSets = self.getAnalysisSets(dateStr,hourInt,strainStr,viewStr)
        larvaeResult = self.larvaeInFunnelNorm(anaSets)
        yawList = list()
        pitchList = list()
        crawlList = list()
        heightList = list()
        for index, row in larvaeResult.iterrows():
            self.pupos = analysePupaePosition.analysePupaePosition(row) 
            yaw_deg, pitch_deg, crawlLen_mm, height_mm = self.pupos.pixelPos2FunnelPos()
            yawList.append(yaw_deg)
            pitchList.append(pitch_deg)
            crawlList.append(crawlLen_mm)
            heightList.append(height_mm)
        larvaeResult['yaw_deg'] = yawList
        larvaeResult['pitch_deg'] = pitchList
        larvaeResult['crawlLen_mm'] = crawlList
        larvaeResult['height_mm'] = heightList
        return larvaeResult
    
    def analyseExperiment(self,dateStr,hourInt,strainStr):
        dfList = list()
        for  viewStr in ['left','right','slope','ortho']:
            dfList.append(self.larvaPosAna(dateStr,hourInt,strainStr,viewStr))
        return pd.concat(dfList)
    
    def analyse(self):
        self.makeSingleExpID()
        resultList = list()
        for expID in tqdm(self.df['expID'].unique()):
            dateStr,hourStr,strainStr = expID.split('|')
            resultList.append(self.analyseExperiment(dateStr,int(hourStr),strainStr))

        self.result = pd.concat(resultList)

    
    def makeSingleExpID(self):
        expID = list()
        for row in self.df.iterrows():
            expID.append(f'{row[1]["date"]}|{row[1]["hour"]}|{row[1]["genType"]}')
        self.df['expID'] = expID

if __name__ ==  '__main__':
       
    dateStr = '2020_06_23'
    hourInt = 16
    strain  = 'pzlok' 
    anaObj = larvaePosAna('/media/gwdg-backup/BackUp/Paul_Funnel/resultDataFrame.h5')
    anaObj.analyse()