

import threading
import queue
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.lines as line
import numpy as np
from scipy import fftpack
from scipy import signal
from rtlsdr import *
import time

cos = np.cos
sin = np.sin
lg = np.log10
plot = plt.plot
fft = fftpack.fft
pi = np.pi

N = 4*1024
data = np.arange(0,N,1)

# plot the spectra

fig = plt.figure()
ax = plt.axes(xlim=(0,N),ylim=(-60,0))#
line, = ax.plot([], [], lw=2)

def init():
    line.set_data([], [])
    return line,

def animate(i):
	x = np.arange(len(data))
	X = data
	line.set_data(x, X)
	return line,

anim = animation.FuncAnimation(fig, animate, frames=1, interval=100, blit=False)



Q = queue.Queue()
sdr = RtlSdr()
window = signal.hamming(N)

def data_processing():
	global Q
	global data
	global window
	
	while  1:
		origin_data = Q.get()
		while not Q.empty():
			Q.get()
		window_data = origin_data*window
		ob_data = abs(fftpack.fft(window_data))
		#sdata=fftpack.fftshift(fftpack.fft(ob_data,overwrite_x=True))
		data = 20*lg(ob_data/N)

def rtlsdr_callback(samples, rtlsdr_obj):
    global Q
    Q.put(samples)

def rtlsdr_main():
	print('Config RTLSDR parameters')
	sdr.rs = 1e6
	sdr.fc = 105.6e6
	sdr.gain = 50
	print('  sample rate: %0.6f MHz' % (sdr.rs/1e6))
	print('  center frequency %0.6f MHz' % (sdr.fc/1e6))
	print('  gain: %d dB' % sdr.gain)
	sdr.read_samples_async(rtlsdr_callback, N)

t1 = threading.Thread(target = data_processing)
t2 = threading.Thread(target = rtlsdr_main)



t1.start()
t2.start()

plt.show()

sdr.cancel_read_async()
sdr.close()

print('ended')

