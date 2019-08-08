

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
index = 2
Down_factor = 20
j = np.complex(0,1)

n = np.arange(N)
t = n/fs
inSig = sin(2*pi*fi*t)
x = cos(2*pi*fc*t+index*inSig)+j*sin(2*pi*fc*t+index*inSig)
xdecimate = signal.decimate(x,Down_factor,ftype="fir")
xangle = np.angle(xdecimate)
xdata = np.diff(xangle)


plt.ylim(-0.02,0.02)
plt.xlim(10,20)
plot(xdata)
plt.show()
