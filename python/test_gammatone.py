#!/usr/bin/env python

# Create input
import scipy
import scipy.signal

# Plotting parameters
plotAngle = False
plotColor = False

# Setup the Gammatone parameters and coefficients # --------------------- #
numFilters = 30
samplerate = 44100

# Frequency parameters
lowFreq = 100.0
highFreq = samplerate / 2.0

# Resolution parameters
c = 9.26449
d = 24.7

def freqs_b_by_freqs(numFilters, lowFreq, highFreq, c, d, order = 1):
    # Find the center frequencies of the filters from the begin and end frequencies
    EarQ = c
    minBW = d
    vec = scipy.arange(numFilters, 0, -1)
    freqs = -(EarQ*minBW) + scipy.exp(vec*(-scipy.log(highFreq + EarQ*minBW) + scipy.log(lowFreq + EarQ*minBW))/numFilters) * (highFreq + EarQ*minBW);
    
    ERB = scipy.power((scipy.power((freqs/EarQ), order) + scipy.power(minBW, order)), (1.0 / order))
    B = 1.019 * 2.0 * scipy.pi * ERB
    
    return (freqs, B)
    
def filter_coeffs_gammatone(freqs, B, samplerate):
    T = 1 / float(samplerate)
    A0 = T
    A2 = 0.0
    B0 = 1.0
    B1 = -2.0 * scipy.cos(2.0 * freqs * scipy.pi * T) / scipy.exp(B * T)
    B2 = scipy.exp(-2.0 * B * T)
    
    A11 = -(2.0 * T * scipy.cos(2.0 * freqs * scipy.pi * T) / scipy.exp(B * T) + 2.0 * \
            scipy.sqrt(3+2.0**1.5) * T * scipy.sin(2.0 * freqs * scipy.pi * T) /  scipy.exp(B * T))/2.0
    
    A12 = -(2.0 * T * scipy.cos(2.0 * freqs * scipy.pi * T) / scipy.exp(B * T) - 2.0 * \
            scipy.sqrt(3+2.0**1.5) * T * scipy.sin(2.0 * freqs * scipy.pi * T) /  scipy.exp(B * T))/2.0
    
    A13 = -(2.0 * T * scipy.cos(2.0 * freqs * scipy.pi * T) / scipy.exp(B * T) + 2.0 * \
            scipy.sqrt(3-2.0**1.5) * T * scipy.sin(2.0 * freqs * scipy.pi * T) /  scipy.exp(B * T))/2.0
    
    A14 = -(2.0 * T * scipy.cos(2.0 * freqs * scipy.pi * T) / scipy.exp(B * T) - 2.0 * \
            scipy.sqrt(3-2.0**1.5) * T * scipy.sin(2.0 * freqs * scipy.pi * T) /  scipy.exp(B * T))/2.0
    
    gain = abs((-2.0 * scipy.exp(4 * 1j * freqs * scipy.pi * T) * T + \
                2.0 * scipy.exp(-(B * T) + 2.0 * 1j * freqs * scipy.pi * T) * T * \
                (scipy.cos(2.0 * freqs * scipy.pi * T) - scipy.sqrt(3 - 2.0**(3/2.0)) *  \
                 scipy.sin(2.0 * freqs * scipy.pi * T)))  *  \
               (-2.0 * scipy.exp(4 * 1j * freqs * scipy.pi * T) * T + \
                2.0 * scipy.exp(-(B * T) + 2.0 * 1j * freqs * scipy.pi * T) * T *  \
                (scipy.cos(2.0 * freqs * scipy.pi * T) + scipy.sqrt(3 - 2.0**(3/2.0))  *  \
                 scipy.sin(2.0 * freqs * scipy.pi * T))) *  \
               (-2.0 * scipy.exp(4 * 1j * freqs * scipy.pi * T) * T + \
                2.0 * scipy.exp(-(B * T) + 2.0 * 1j * freqs * scipy.pi * T) * T *  \
                (scipy.cos(2.0 * freqs * scipy.pi * T) - \
                 scipy.sqrt(3 + 2.0**(3/2.0)) * scipy.sin(2.0 * freqs * scipy.pi * T)))  *  \
               (-2.0 * scipy.exp(4 * 1j * freqs * scipy.pi * T) * T + 2.0 * scipy.exp(-(B * T) + 2.0 * 1j * freqs * scipy.pi * T) * T *  \
                (scipy.cos(2.0 * freqs * scipy.pi * T) + scipy.sqrt(3 + 2.0**(3/2.0)) * scipy.sin(2.0 * freqs * scipy.pi * T)))  /  \
               (-2.0  /  scipy.exp(2.0 * B * T) - 2.0 * scipy.exp(4 * 1j * freqs * scipy.pi * T) +  \
                2.0 * (1 + scipy.exp(4 * 1j * freqs * scipy.pi * T)) / scipy.exp(B * T))**4)
    
    allfilts = scipy.ones(len(freqs))
    fcoefs = (A0 * allfilts, A11, A12, A13, A14, A2 * allfilts, B0 * allfilts, B1, B2, gain)
    return fcoefs
        
freqs, B = freqs_b_by_freqs(numFilters, lowFreq, highFreq, c, d)
(B0, B11, B12, B13, B14, B2, A0, A1, A2, gain) = filter_coeffs_gammatone(freqs, B, samplerate)
# -------------------------------------------------------- #


import ricaudio

coeffsB1 = scipy.array(scipy.vstack((B0, B11, B2)) / gain, dtype = 'f4')
coeffsB2 = scipy.array(scipy.vstack((B0, B12, B2)), dtype = 'f4')
coeffsB3 = scipy.array(scipy.vstack((B0, B13, B2)), dtype = 'f4')
coeffsB4 = scipy.array(scipy.vstack((B0, B14, B2)), dtype = 'f4')

coeffsA = scipy.array(scipy.vstack((A0, A1, A2)), dtype = 'f4')

npoints = 10000
w = scipy.arange(-scipy.pi, scipy.pi, 2*scipy.pi/(npoints), dtype = 'f4')

d1 = ricaudio.freqz(coeffsB1, coeffsA, w)
d2 = ricaudio.freqz(coeffsB2, coeffsA, w)
d3 = ricaudio.freqz(coeffsB3, coeffsA, w)
d4 = ricaudio.freqz(coeffsB4, coeffsA, w)

d = d1 * d2 * d3 * d4

# Plot the frequency response
import pylab

subplots = 2 if plotAngle else 1;
    

pylab.subplot(subplots,1,1)
if plotColor:
    pylab.plot(w[npoints/2:], abs(d[npoints/2:,:]))
else:
    pylab.plot(w[npoints/2:], abs(d[npoints/2:,:]), c = 'black')
    
pylab.title('Magnitude of the Frequency Response of a \n Gammatone Filterbank implementation')

pylab.gca().set_xlim([0, scipy.pi])

if plotAngle:
    pylab.subplot(2,1,2)
    if plotColor:
        pylab.plot(w[npoints/2:], scipy.angle(d[npoints/2:,:]))
    else:
        pylab.plot(w[npoints/2:], scipy.angle(d[npoints/2:,:]), c = 'black')
    pylab.title('Angle of the Frequency Response')
    
    pylab.gca().set_xlim([0, scipy.pi])
    
pylab.show()

