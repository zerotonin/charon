
import matplotlib.pyplot as plt     
import numpy as np
import scipy.optimize
from tqdm import tqdm

class graviStumps():

    def __init__(self,stumpType ='large'):

        self.yawAngle       = np.array([0   ,    45,    90,   135,   180,   225,   270,   315,  360],dtype=float)
        if stumpType == 'large':
            self.pitchAngle = np.array([90  , 86.03977342, 76.70142967, 67.02602285, 64.69862137, 67.02602285, 76.70142967, 86.03977342, 90],dtype=float)
            self.lengthMM   = np.array([55.0, 55.13164150, 56.51548460, 59.30853371, 60.83584470, 59.30853371, 56.51548460, 55.13164150, 55.0],dtype=float)
        elif stumpType == 'small':
            self.pitchAngle = np.array([90  , 84.56238130, 71.99583839, 60.97806217, 56.97613244, 60.97806217, 71.99583839, 84.56238130, 90],dtype=float)
            self.lengthMM   = np.array([40.0, 40.18081522, 42.05948169, 45.74387446, 47.70744177, 45.74387446, 42.05948169, 40.18081522, 40.0],dtype=float)
        else:
            raise ValueError(f'graviStumps:__init__: stump type unknown: {stumpType}')

        self.funcPitch  = self.fit_yawAngleBased(self.yawAngle,self.pitchAngle,'cos')
        self.funcLength = self.fit_yawAngleBased(self.yawAngle,self.lengthMM,'gauss')
    
    def fit_yawAngleBased(self,tt, yy,type='sin'):
        '''Fit sin to the input time sequence, and return fitting parameters "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc"'''
        tt = np.array(tt)
        yy = np.array(yy)
        ff = np.fft.fftfreq(len(tt), (tt[1]-tt[0]))   # assume uniform spacing
        Fyy = abs(np.fft.fft(yy))
        guess_freq = abs(ff[np.argmax(Fyy[1:])+1])   # excluding the zero frequency "peak", which is related to offset
        guess_amp = np.std(yy) * 2.**0.5
        guess_offset = np.mean(yy)
        guess = np.array([guess_amp, 2.*np.pi*guess_freq, 0., guess_offset])
        if type == 'sin':
            def fitfunc(t, A, w, p, c):  return  A * np.sin(w*t + p) + c
            popt, pcov = scipy.optimize.curve_fit(fitfunc, tt, yy, p0=guess)
            A, w, p, c = popt
        elif type == 'cos':
            def fitfunc(t, A, w, p, c):  return A * np.cos(w*t + p) + c
            popt, pcov = scipy.optimize.curve_fit(fitfunc, tt, yy, p0=guess)
            A, w, p, c = popt
        elif type == 'gauss':
            n = len(yy)                          #the number of data
            mean = sum(tt*yy)/n                   #note this correction
            sigma = np.sqrt(sum(yy*(tt-mean)**2)/n)      #note this correction
            def fitfunc(x, a, x0, sigma,d): return a*np.exp(-(x-x0)**2/(2*sigma**2))+d
            popt, pcov = scipy.optimize.curve_fit(fitfunc, tt, yy, bounds=(0,[1,mean,sigma,55]), method='dogbox')
            a, x0, sigma,d = popt
            print(d)

        if type == 'sin':
            resfunc = lambda t: A * np.sin(w*t + p) + c
        elif type == 'cos':
            resfunc = lambda t: A * np.cos(w*t + p) + c
        elif type == 'gauss':
            resfunc = lambda x: a*np.exp(-(x-x0)**2/(2*sigma**2))+d
        return  resfunc

    def plotFitFunc(self):
        x_data = np.linspace(0,360,1000)
        plt.figure(figsize=(6, 4))
        plt.scatter(self.yawAngle, self.pitchAngle, label='pitchAngle')
        plt.plot(x_data,self.funcPitch(x_data)    , label='Fitted function')
        plt.figure(figsize=(6, 4))
        plt.scatter(self.yawAngle, self.lengthMM  , label='sideLength')
        plt.plot(x_data,self.funcLength(x_data)   , label='Fitted function') 

        plt.legend(loc='best')

        plt.show()

x = graviStumps('large')
x.plotFitFunc()