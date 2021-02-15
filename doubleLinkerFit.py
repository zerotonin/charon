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
    #       exp(-z ⋅ a + b)  
    # y = ───────────────────
    #     1 + exp(-z ⋅ a + b)
    
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
    #return (np.exp(-((m0-((Cch/(Cch+Csp**2))*D**2))/kT)))/(1+(np.exp(-((m0-((Cch/(Cch+Csp**2))*D**2))/kT))))
    return (np.exp(-((m0-((Cch/Csp**2)*D**2))/kT)))/(1+(np.exp(-((m0-((Cch/Csp**2)*D**2))/kT))))

def channelFuncSimplified(D,m0,C):

    kT = 4.1
    return (np.exp(-((m0-((C/C**2)*D**2))/kT)))/(1+(np.exp(-((m0-((C/C**2)*D**2))/kT))))
  
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
    elif len(popt) == 2:
        labelStr = 'fit for ' +dataStr+ ': m0=%5.3f, C=%5.3f' % tuple(popt)
        plt.plot(data[:,0], channelFuncSimplified(data[:,0], *popt),color=col,label= labelStr)
    else:
        labelStr = 'fit for ' +dataStr+ ': a=%5.3f,b=%5.3f' % tuple(popt)
        plt.plot(data[:,0], simpleSigmoid(data[:,0], *popt),color=col,label= labelStr)


def finalisePlot():
    plt.xlabel('absolute pressure stimulus, mmHq')
    plt.ylabel('normalised cell response, aU')
    plt.legend(loc='upper left',fancybox=True, shadow=True)
    plt.show()

def quickFit(wt,dl,funcName,p0=[1,400,400],bounds=(0.0001, [3000.,10000.,1000]),method="lm",maxfev=100000000):
    if funcName == 'channelFunc':
        wt_popt, wt_pcov = curve_fit(channelFunc, wt[:,0], wt[:,1],p0=p0,bounds=bounds,method=method,maxfev=maxfev)
        dl_popt, dl_pcov = curve_fit(channelFunc, dl[:,0], dl[:,1],p0=p0,bounds=bounds,method=method,maxfev=maxfev)
    elif funcName == 'simpleSigmoid':
        wt_popt, wt_pcov = curve_fit(simpleSigmoid, wt[:,0], wt[:,1],p0=p0,bounds=bounds,method=method,maxfev=maxfev)
        dl_popt, dl_pcov = curve_fit(simpleSigmoid, dl[:,0], dl[:,1],p0=p0,bounds=bounds,method=method,maxfev=maxfev)
    return (wt_popt,wt_pcov,dl_popt,dl_pcov)

def quickReport(wt,dl,fitResult):
    plt.figure()
    plotRawData(wt,dl)
    plotFit(wt,fitResult[0],'wt','lightgray')
    plotFit(dl,fitResult[2],'dl','dimgray')
    if len(fitResult[0]) ==3:
        plotFit(dl,[fitResult[0][0],fitResult[0][1]/2,fitResult[0][2]*2],'dl double','blue')
    finalisePlot()


# ██████  ██    ██ ███    ██     ███████ ██ ████████ ███████ 
# ██   ██ ██    ██ ████   ██     ██      ██    ██    ██      
# ██████  ██    ██ ██ ██  ██     █████   ██    ██    ███████ 
# ██   ██ ██    ██ ██  ██ ██     ██      ██    ██         ██ 
# ██   ██  ██████  ██   ████     ██      ██    ██    ███████ 


# import the raw data
wt,dl = importData()
##dl = np.vstack((np.array([0.001,0.001]),dl,np.array([175.,1.])))


# preform simple fit
fitResult = quickFit(wt,dl,'channelFunc',p0=[15,15,15],bounds=(0.0001, [10000.,10000.,1000]),method="trf",maxfev=100000000)
#fitResult = quickFit(wt,dl,'simpleSigmoid',p0=[200,40],bounds=(0.0001, [10000000.,10000000.]),method="trf",maxfev=100000000)
quickReport(wt,dl,fitResult)    
# plot result

'''

#
samples = 100
trialCch = np.geomspace(0.001,10000,samples,endpoint=True)
trialCsp = np.geomspace(0.001,10000,samples,endpoint=True)
resres = np.zeros(shape=(samples,samples))
for CchI in range(1,samples):
    for CspI in range(1,samples):
        res = channelFunc(wt[:,0],25.223,trialCch[CchI],trialCsp[CspI])
        #res = channelFuncSimplified(wt[:,0],trialCch[CchI],trialCsp[CspI])
        resres[CchI,CspI] = np.nansum((wt[:,1]-res)**2)

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

# Set up grid and test data
x = trialCch
y = trialCsp


hf = plt.figure()
#ha = hf.add_subplot(111, projection='3d')

X, Y = np.meshgrid(x, y)  # `plot_surface` expects `x` and `y` data to be 2D
#ha.plot_surface(X, Y, resres, cmap=cm.inferno)
plt.pcolormesh(X, Y, resres, cmap=cm.inferno)
plt.xscale("log")
plt.yscale("log")

hf = plt.figure()
ha = hf.add_subplot(111, projection='3d')

X, Y = np.meshgrid(x, y)  # `plot_surface` expects `x` and `y` data to be 2D
ha.plot_surface(X, Y, resres, cmap=cm.inferno)
ha.set_xscale('log')
ha.set_yscale('log')

plt.show()
'''