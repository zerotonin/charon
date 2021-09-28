
import matplotlib.pyplot as plt     
import numpy as np
import scipy.optimize
from tqdm import tqdm

class graviStumps():

    def __init__(self,stumpType ='large'):

        self.yawAngle       = np.array([0   ,    45,    90,   135,   180,   225,   270,   315,  360],dtype=float)
        if stumpType == 'large':
            self.pitchAngle = np.array([90  ,    87,    77,    67,    65,    67,    77,    87,   90],dtype=float)
            self.lengthMM   = np.array([55.0, 55.06, 56.52, 59.75, 60.84, 59.75, 56.62, 55.06, 55.0],dtype=float)
        elif stumpType == 'small':
            self.pitchAngle = np.array([90  ,    84,    72,    61,    57,    61,    72,    84,   90],dtype=float)
            self.lengthMM   = np.array([40.0, 40.23, 42.06, 45.52, 47.71, 45.52, 42.06, 40.23, 40.0],dtype=float)
        else:
            raise ValueError(f'graviStumps:__init__: stump type unknown: {stumpType}')

        fitResultPitch  = self.fit_sin(self.yawAngle,self.pitchAngle)
        self.funcPitch  = fitResultPitch['fitfunc']
        fitResultLength = self.fit_sin(self.yawAngle,self.lengthMM)
        self.funcLength = fitResultLength['fitfunc']
    
    def fit_sin(self,tt, yy):
        '''Fit sin to the input time sequence, and return fitting parameters "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc"'''
        tt = np.array(tt)
        yy = np.array(yy)
        ff = np.fft.fftfreq(len(tt), (tt[1]-tt[0]))   # assume uniform spacing
        Fyy = abs(np.fft.fft(yy))
        guess_freq = abs(ff[np.argmax(Fyy[1:])+1])   # excluding the zero frequency "peak", which is related to offset
        guess_amp = np.std(yy) * 2.**0.5
        guess_offset = np.mean(yy)
        guess = np.array([guess_amp, 2.*np.pi*guess_freq, 0., guess_offset])

        def sinfunc(t, A, w, p, c):  return A * np.sin(w*t + p) + c
        popt, pcov = scipy.optimize.curve_fit(sinfunc, tt, yy, p0=guess)
        A, w, p, c = popt
        f = w/(2.*np.pi)
        fitfunc = lambda t: A * np.sin(w*t + p) + c
        return {"amp": A, "omega": w, "phase": p, "offset": c, "freq": f, "period": 1./f, "fitfunc": fitfunc, "maxcov": np.max(pcov), "rawres": (guess,popt,pcov)}
