# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 00:50:45 2023

Returns the skive window width and the tip width if a wire diameter is provided

Refer to the following lines for more on convolution
https://en.wikipedia.org/wiki/Convolution
https://betterexplained.com/articles/intuitive-convolution/

@author: Nelson To
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

#pre-process data
# data = np.genfromtxt("Data\wireDiameter-20230329-102112_FX-2-2032.csv", skip_header=1, dtype='float', delimiter=',')
# data = np.delete(data, slice(0,8), axis=1)
    
def skiveMeasure(wireDiameter_raw):
    v = np.array([-1, 0 , 1])
    wireDiameter = np.array(wireDiameter_raw)
    
    convVector = np.convolve(wireDiameter, v, mode='full')
    wireDiameterFlip = np.flipud(wireDiameter)
    convVectorFlip = np.convolve(wireDiameterFlip, v, mode='full')
    
    x=np.arange(0,(0.03*len(wireDiameter)),0.03)
    
    peaks = find_peaks(convVector[:len(wireDiameter)], height=0.01, prominence=0.02)[0]
    peaksFlip = find_peaks(convVectorFlip[:len(wireDiameter)], height=0.01, prominence=0.02)[0]
    
    print ( "wire index:" + str(len(x)) + " peak indexes:" + str(peaks) + " " + str(peaksFlip))
    
    loc = np.append(x[peaks],x[-1]-x[peaksFlip])
    
    if len(loc) == 2:
        return loc[1]-loc[0], loc[0]
    else:
        plt.plot(x, wireDiameter)
        plt.vlines(x = loc, ymin = min(wireDiameter), ymax = max(wireDiameter), color = 'b')
        plt.show()
        return "N/A","N/A"

