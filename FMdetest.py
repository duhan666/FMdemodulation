

import numpy as np
import matplotlib.pyplot as plt 
from scipy import fftpack
from scipy import signal


cos = np.cos
sin = np.sin
lg = np.log10
plot = plt.plot
fft = fftpack.fft
pi = np.pi

N = 1024
fc = 100e6
fi = 44e3
fs = 1e6
index = 1
j = np.complex(0,1)

n = np.arange(N)
t = n/fs
inSig = sin(2*pi*fi*t)+sin(3*pi*fi*t)+sin(5*pi*fi*t)
x = cos(2*pi*fc*t+index*inSig)+j*sin(2*pi*fc*t+index*inSig)
xdecimate = signal.decimate(x,Down_factor,ftype="fir")
xangle = np.angle(x)
xdata = np.gradient(xangle)

plt.subplot(2,1,1)
#plt.ylim(-0.02,0.02)
plt.xlim(0,0.0002)

plot(t,xdata)
plt.subplot(2,1,2)
plot(t,inSig)
plt.xlim(0,0.0002)

plt.show()
