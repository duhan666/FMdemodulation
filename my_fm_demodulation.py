import threading
import queue
import numpy as np
from scipy import fftpack
from scipy import signal
from rtlsdr import *
import pyaudio

N = 512*10
RFRATE = 0.25e6
RFFREQ = 101.1e6
RFGAIN = 50
DOWN_FACTOR = 10
AUDIOSIZE = int(N/DOWN_FACTOR)
FORMAT = pyaudio.paInt16
AUDIORATE = int(RFRATE/DOWN_FACTOR)
CHANNELS = 1

audioQ = queue.Queue()
dataQ = queue.Queue()
sdr = RtlSdr()
window = signal.hamming(N)

def rtlsdr_callback(samples, rtlsdr_obj):
    global Q
    dataQ.put(samples)

def rtlsdr_thread():
	global sdr
	print('Config RTLSDR parameters')
	sdr.rs = 1e6
	sdr.fc = 105.6e6
	sdr.gain = 50
	print('  sample rate: %0.6f MHz' % (sdr.rs/1e6))
	print('  center frequency %0.6f MHz' % (sdr.fc/1e6))
	print('  gain: %d dB' % sdr.gain)
	sdr.read_samples_async(rtlsdr_callback, N)
	sdr.cancel_read_async()
	sdr.close()
	print('read rtlsdr thread ended')


def dem_data_thread():
	pre_data = 0
	while not dataQ.empty():
		data = dataQ.get()
		angle_data=np.angle(data)
		audioda=np.diff(angle_data)
		audiodata=np.insert(audioda,0,angle_data[0]-pre_data)
		pre_data=angle_data[-1]
		audiodata=np.unwrap(audiodata,np.pi)
		audiodata = audiodata[0::DOWN_FACTOR]
		audiodata_amp=audiodata*5e3
		snd_data = audiodata_amp.astype(np.dtype('<i2')).tostring()
		audioQ.put(snd_data)


def audio_callback():
	global audioQ
	return (audioQ.get(),pyaudio.paContinue)


p = pyaudio.PyAudio()
print("SoundCard Output @ %d KHz" % (AUDIORATE/1e3))
stream = p.open(format=FORMAT,
     			channels=CHANNELS,
            	rate=AUDIORATE,
            	input=False,
           		output=True,
           	 	frames_per_buffer=AUDIOSIZE,
            	stream_callback=audio_callback)
stream.start_stream()



if __name__ == '__main__':

    t_data_demodulation = threading.Thread(target=dem_data_thread)
    t_rtlsdr = threading.Thread(target=rtlsdr_thread)

    t_data_demodulation.start()
    t_rtlsdr.start()


    stream.stop_stream()
    stream.close()