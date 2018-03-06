import math
import numpy as np
from detect_peaks import *

def doCalc(V_1, I_1, si, ap):

    '''
    :param V:       A single voltage trace
    :param I:       A single current trace
    :param si:      sampling interval in us calculated prior
    :param ap:      analysis parameters dictionary
    :return: STA
    :return: G
    :return: phi
    :return: freq
    :return: spBins
    '''


    siSec = si*1e-6
    fs = 1/siSec
    wPoints = math.floor((ap['rv']['window']/1000.)/siSec)
    nLength = math.floor((ap['rv']['length']/siSec))/wPoints
    spBins = np.array([0] * int(nLength))

    STA = []
    staWindow = int(math.floor((ap['rv']['STAwindow']*1e-3)/siSec))
    G = []; phi = []; freq = []

    # filter the voltage trace to avoid spurious peaks due to noise
    V_1 = np.convolve(V_1, ap['rv']['f'], 'same')/(len(ap['rv']['f']-1))

    T = np.array(range(0, len(V_1)))/fs
    spInd = detect_peaks(V_1, mph=ap['rv']['threshold'])
    dcCurrentTime = ap['rv']['prefix'] + ap['rv']['length']
    dcSamples = np.where((T > dcCurrentTime) & (T < dcCurrentTime + ap['rv']['currentLength']))
    I_1 = (I_1 - np.mean(I_1[dcSamples])).tolist()

    if len(spInd) > 0:
        # Get the times of the spikes
        tSpikes = T[spInd]
        k = np.floor((tSpikes-ap['rv']['prefix'])*1000/ap['rv']['window'])
        k = k.astype(int)

        if len(np.where(k > nLength)[0]) > 0:
            b = np.asscalar(np.min(np.where(k > nLength)))
            k = k[0:b]

        spBins[k] = 1

        for j in range(0, len(spInd)):
            ind = range(spInd[j]-staWindow, spInd[j])
            if min(ind) > 0:
                STA.append(I_1[(spInd[j]-staWindow):spInd[j]])

        STA = np.array(STA)

        # if ap['rv']['computeGain'] == True:
            # Perform the frequency dependent gain calculation --- still need to work hard to translate the freqDepGain function (goertzel algorithm) to python
            # tind = np.where((T >= ap['rv']['prefix']) & (T < ap['rv']['prefix'] + ap['rv']['length']))
            # voltage = V[tind]
            # current = np.array(I)[tind]
            # [G, phi, freq] = freqDepGain(voltage, current, fs, ap)
    else:
        STA = np.empty


    return STA, G, phi, freq, spBins