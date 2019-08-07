
import numpy as np
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
import pyaudio
import pyaudio
import wave
import threading
import queue
import time
from scipy import signal

plot = plt.plot

WIDTH = 2
CHANNELS = 1
RATE = 44100

Q = queue.Queue()

data = []
window = signal.hamming(1024)


def audio_callback(in_data, frame_count, time_info, status):
    Q.put(in_data)
    return (None,pyaudio.paContinue)

def audio_read(stream):
	global data
	global Q

	while stream.is_active():
		if Q.empty():
			time.sleep(0.1)
		else:
			a = Q.get()
			data = np.frombuffer(a,np.dtype('int16'))
		print(Q.qsize())

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=False,
                stream_callback=audio_callback)

stream.start_stream()
time.sleep(0.1)

t = threading.Thread(target = audio_read,args=(stream,))

t.start()

# PLOT
fg = plt.figure()
ax = plt.axes(xlim=(0,len(data)), ylim=(-10000,10000))
line, = ax.plot([], [], lw=2)

def init():
	line.set_data([],[])
	return line,

def updata_fig(i):
	global data
	x = np.arange(len(data))
	y = data*window
	line.set_data(x,y)
	return line,

ani = animation.FuncAnimation(fg, 
                              updata_fig,
                              init_func=init, 
                              frames=1,
                              interval=100,
                              blit=True)

plt.show()

stream.stop_stream()
stream.close()
p.terminate()





