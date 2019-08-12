

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

Down_factor = 10
N = 5120
fc = 0
fi = 44e3
fs = fi*1280
index = 40000
j = np.complex(0,1)

n = np.arange(N)
t = n/fs
inSig = cos(2*pi*fi*t)#+cos(3*pi*fi*t)
x = cos(2*pi*fc*t+index*inSig)+j*sin(2*pi*fc*t+index*inSig)
xdecimate = signal.decimate(x,Down_factor,ftype="fir")
xangle = np.angle(x)
xdata = np.gradient(xangle)
xdata = np.unwrap(xdata)

plt.subplot(4,1,1)
#plt.ylim(-0.02,0.02)
#plt.xlim(0,0.0002)
plot(t,xdata)
plt.subplot(4,1,2)
plot(x.real)
plt.subplot(4,1,3)
plot(x.imag)

plt.subplot(4,1,4)
plot(t,inSig)
#plt.xlim(0,0.0002)

plt.show()
