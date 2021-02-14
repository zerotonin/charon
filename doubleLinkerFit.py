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


def channelFunc(D,m0,Cch,Csp):
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

def plotFit(data,popt,labelStr,col ='r'):
    plt.plot(data[:,0], channelFunc(data[:,0], *popt),color=col,label= 'fit for ' +labelStr+ ': m0=%5.3f, Cch=%5.3f, Csp=%5.3f' % tuple(popt))

def finalisePlot():
    plt.xlabel('absolute pressure stimulus, mmHq')
    plt.ylabel('normalised cell response, aU')
    plt.legend()
    plt.show()

wt,dl = importData()

popt, pcov = curve_fit(channelFunc, wt[:,0], wt[:,1], bounds=(0, [100000., 100000., 100000.]))




plotRawData(wt,dl)
plotFit(wt,popt,'wt')
finalisePlot()