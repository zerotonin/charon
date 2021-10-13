import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

class paulPlots():
    def __init__(self,dfPos = '/media/gwdg-backup/BackUp/Paul_Funnel/analysisDataFrame.h5'):
        self.df = pd.read_hdf(dfPos, key='df')
        self.typoCorrection()
        self.df.reset_index(inplace=True)
        self.df = self.df.dropna()
        self.df = self.df.drop_duplicates()
        self.strainList = self.df['genType'].unique()
        self.lightCond  = self.df['light'].unique()

    def getAnalysisSets(self,strainStr,lightStr):
        strainSet = self.df.loc[self.df['genType'] == strainStr]
        strainSet = strainSet.loc[strainSet['light'] == lightStr]
        return strainSet.copy(deep =True)
    
    def typoCorrection(self):
        self.df.loc[self.df['genType'] == 'cantons','genType']  = 'cantonS'
        self.df.loc[self.df['genType'] == 'canons','genType']   = 'cantonS'
        self.df.loc[self.df['genType'] == 'contans','genType']  = 'cantonS'
        self.df.loc[self.df['genType'] == 'pzlescue','genType'] = 'pzlrescue'
        self.df.loc[self.df['genType'] == 'nan36aM','genType']  = 'nan36a'
        self.df.loc[self.df['genType'] == 'pzlok','genType']  = 'pzlko'

    def getNaNIavSet(self):
        dfList = list()
        for strainStr in ['cantonS','iav','nan36a','iavrescue']:
            dfList.append(self.df.loc[self.df['genType'] == strainStr])
        return pd.concat(dfList)

    def getPZLSet(self):
        dfList = list()
        for strainStr in ['cantonS','pzlko','pzlrescue','tm6bpzl']:
            dfList.append(self.df.loc[self.df['genType'] == strainStr])
        return pd.concat(dfList)

    def strainHistogram(self,plotDf,dataCol):
        sns.displot(plotDf, x=dataCol, hue="genType", stat="density", multiple="dodge", common_norm=False)

    def lightBoxPlots(self):
        
        for dataCol in ['pitch_deg','crawlLen_mm','height_mm']:
            plt.figure()
            sns.boxplot(x="genType", y=dataCol,
                hue="light", palette=["dimgray", "w"], notch=True,
                data=self.df)

    def strainBoxPlots(self,df,pall):
        
        for dataCol in ['pitch_deg','crawlLen_mm','height_mm']:
            plt.figure()
            sns.boxplot(x="genType", y=dataCol,
                palette=pall,notch=True, data=df)

    def  multipage(self,filename, figs=None, dpi=200):
        pp = PdfPages(filename)
        if figs is None:
            figs = [plt.figure(n) for n in plt.get_fignums()]
        for fig in figs:
            fig.savefig(pp, format='pdf')
        pp.close()



#if __name__ ==  '__main__':
plotObj = paulPlots()
print(plotObj.strainList)
plotObj.lightBoxPlots()
df = plotObj.getNaNIavSet()
df = df.drop_duplicates()
for dataCol in ['pitch_deg','crawlLen_mm','height_mm']:
    plotObj.strainHistogram(plotObj.df,dataCol)

df2= plotObj.getPZLSet()
df2= df2.drop_duplicates()
plotObj.strainBoxPlots(df,sns.color_palette())
plotObj.strainBoxPlots(df2,'pastel')
plotObj.multipage('/media/gwdg-backup/BackUp/Paul_Funnel/figures.pdf')
plotObj.df.to_csv('/media/gwdg-backup/BackUp/Paul_Funnel/anaData.csv')
plt.show()