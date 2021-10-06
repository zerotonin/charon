import pandas as pd

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
        print(viewSet)
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
        larvaeFunnelNorm = self.larvaeInFunnelNorm(anaSets)
        print(anaSets[0],larvaeFunnelNorm)

if __name__ ==  '__main__':
       
    dateStr = '2020_06_23'
    hourInt = 16
    strain  = 'pzlok' 
    viewStr = 'left'
    x = larvaePosAna('/media/gwdg-backup/BackUp/Paul_Funnel/resultDataFrame.h5')
    x.larvaPosAna(dateStr,hourInt,strain,viewStr)
