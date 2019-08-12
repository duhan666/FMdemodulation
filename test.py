





import numpy as np
from scipy import fftpack
import matplotlib.pyplot as plt



cos = np.cos
sin = np.sin
pi = np.pi
lg = np.log10


fi = 100e3
fs = 500e3
N = 1024

n = np.arange(N)
t = n/fs
x = sin(2*pi*fi*t)
X = 20*lg(abs(fftpack.fft(x))/N)


plt.plot(X)
plt.show()