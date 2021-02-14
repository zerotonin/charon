# This module was designed to evaluate the usability of different fits
# for observations during patch clamp recordings. The recorded cells expressed
# the nompC-mechanotransducer in the wildtype form or with a duplicated region
# called the "Linker". Hence common abbriviations are wildtype = wt and 
# double-linker = dl.
# The recording data and genetic modification are provided by P/ Hehlert, 
# T. Effertz, and M. Goepfert
#
#
# First fit function provided by M. Goepfert and T. Effertz
# 
# y=(exp(-((m0-((Cch/Csp^2)*D^2))/kT)))/(1+(exp(-((m0-((Cch/Csp^2)*D^2))/kT))))
# 
# m0 : Delta Energy channel closed open maybe around 25ish
# Cch: Channel compliance seed values of 1000 or 300000 work
# Csp: Gating spring compliance seed values of 600 or 11000 work
# kT: Boltzman Konstant at Roomtemperatur ~ 4.1 zJ

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

def simpleSigmoid(z,a,b):
    # This is a simple sigmoid function to test if our curve fitting works.
    #
    #   exp(-z ⋅ a + b)  
    # ───────────────────
    # 1 + exp(-z ⋅ a + b)
    
    return np.exp(-z*a+b)/(1 + np.exp(-z*a+b))


def channelFunc(D,m0,Cch,Csp):
    # This function represents the numpy conform notation of the formula 2.12 on page 20 of:
    # Albert, Jörg T., Björn Nadrowski, and Martin C. Göpfert. "Mechanical signatures of 
    # transducer gating in the Drosophila ear." Current Biology 17.11 (2007): 1000-1006
    #
    #         ⎛ ⎛     ⎛⎛ Cch⎞    2⎞⎞⎞   
    #         ⎜ ⎜m0 - ⎜⎜────⎟ ⋅ D ⎟⎟⎟   
    #         ⎜ ⎜     ⎜⎜   2⎟     ⎟⎟⎟   
    #         ⎜ ⎜     ⎝⎝Csp ⎠     ⎠⎟⎟   
    #     exp ⎜-⎜──────────────────⎟⎟   
    #         ⎝ ⎝        kT        ⎠⎠   
    # y = ─────────────────────────────────
    #         ⎛    ⎛ ⎛     ⎛⎛ Cch⎞    2⎞⎞⎞⎞
    #         ⎜    ⎜ ⎜m0 - ⎜⎜────⎟ ⋅ D ⎟⎟⎟⎟
    #         ⎜    ⎜ ⎜     ⎜⎜   2⎟     ⎟⎟⎟⎟
    #         ⎜    ⎜ ⎜     ⎝⎝Csp ⎠     ⎠⎟⎟⎟
    #     1 + ⎜exp ⎜-⎜──────────────────⎟⎟⎟
    #         ⎝    ⎝ ⎝        kT        ⎠⎠⎠
    #
    # D  =  Stimulus amplitude
    # kT =  Boltzman Konstant at Roomtemperatur ~ 4.1 zJ 

    kT = 4.1
    return (np.exp(-((m0-((Cch/Csp**2)*D**2))/kT)))/(1+(np.exp(-((m0-((Cch/Csp**2)*D**2))/kT))))

def readCSVFile():
    # read from csv file
    wt = np.genfromtxt('wt.csv',delimiter=',')
    dl = np.genfromtxt('dl.csv',delimiter=',')
    return wt,dl


def sortDataByFirstColumn(wt,dl):
    #sort by x values
    wt = wt[wt[:,0].argsort(kind='mergesort')]
    dl = dl[dl[:,0].argsort(kind='mergesort')]
    return wt,dl

def importData():
    wt,dl = readCSVFile()
    wt,dl = sortDataByFirstColumn(wt,dl)
    return wt,dl


def plotRawData(wt,dl):

    plt.plot(wt[:,0],wt[:,1],'o',mfc="lightgray",mec="k",label='wildtype data')
    plt.plot(dl[:,0],dl[:,1],'o',mfc="dimgray"  ,mec="k",label='double linker data')

def plotFit(data,popt,dataStr,col ='dimgray'):
    if len(popt) == 3:
        labelStr = 'fit for ' +dataStr+ ': m0=%5.3f, Cch=%5.3f, Csp=%5.3f' % tuple(popt)
        plt.plot(data[:,0], channelFunc(data[:,0], *popt),color=col,label= labelStr)
    else:
        labelStr = 'fit for ' +dataStr+ ': a=%5.3f,b=%5.3f' % tuple(popt)
        plt.plot(data[:,0], simpleSigmoid(data[:,0], *popt),color=col,label= labelStr)


def finalisePlot():
    plt.xlabel('absolute pressure stimulus, mmHq')
    plt.ylabel('normalised cell response, aU')
    plt.legend(loc='upper left',fancybox=True, shadow=True)
    plt.show()



# ██████  ██    ██ ███    ██     ███████ ██ ████████ ███████ 
# ██   ██ ██    ██ ████   ██     ██      ██    ██    ██      
# ██████  ██    ██ ██ ██  ██     █████   ██    ██    ███████ 
# ██   ██ ██    ██ ██  ██ ██     ██      ██    ██         ██ 
# ██   ██  ██████  ██   ████     ██      ██    ██    ███████ 


# import the raw data
wt,dl = importData()
dl = np.vstack((np.array([0.,0.]),dl))
# preform simple fit
popt, pcov = curve_fit(channelFunc, wt[:,0], wt[:,1],p0=[25,1000,600])#, bounds=(0, [1000000., 1000000., 1000000.]))
popt2, pcov2 = curve_fit(channelFunc, dl[:,0], dl[:,1],p0=[25,1000,600])#, bounds=(0, [1000000., 1000000., 1000000.]))
# plot result
plt.figure()
plotRawData(wt,dl)
plotFit(wt,popt,'wt','lightgray')
plotFit(dl,popt2,'dl','gray')
print(popt)
finalisePlot()