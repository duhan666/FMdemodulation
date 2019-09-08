# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 10:48:07 2015
@author: Administrator

https://github.com/licheegh/dig_sig_py_study/blob/master/RTL_PY/fm_radio.py

"""

import threading
import queue
import numpy as np
from scipy import fftpack
from scipy import signal
from rtlsdr import *
import pyaudio

RFRATE = 0.25e6
RFFREQ = 89.7e6
RFGAIN = 50

DOWN_FACTOR = 10

RFSIZE = int(1024*10)
AUDIOSIZE = int(RFSIZE/DOWN_FACTOR)
FORMAT = pyaudio.paInt16
CHANNELS = 1
AUDIORATE = int(RFRATE/DOWN_FACTOR)

tempdata = np.zeros(AUDIOSIZE)

def read_data_thread(rf_q,ad_rdy_ev,audio_q):
    pre_data=0
    print("read data thread start")
    while 1:
        ad_rdy_ev.wait(timeout=1000)
        while not rf_q.empty():
            data=rf_q.get()
 
            xangle = np.angle(data)
            xda = np.diff(xangle)
            xdata = np.insert(xda,0,xangle[0]-pre_data)
            pre_data = xangle[-1]
            xdata = np.unwrap(xdata,np.pi)
            audiodata = signal.decimate(xdata,DOWN_FACTOR,ftype="fir")

            audiodata_amp=audiodata*5e3
            snd_data = audiodata_amp.astype(np.dtype('<i2')).tostring()
            audio_q.put(snd_data)
        ad_rdy_ev.clear()

#rtlsdr
def rtlsdr_callback(samples,rtlsdr_obj):
	global rf_q
	global ad_rdy_ev
	rf_q.put(samples)
	ad_rdy_ev.set()

def rtlsdr_thread(rf_q,ad_rdy_ev):

    print('rtlsdr thread start')
    sdr = RtlSdr()
    sdr.rs = RFRATE
    sdr.fc = RFFREQ
    sdr.gain = RFGAIN
    #sdr.freq_correction = -13
    sdr.set_agc_mode(True)
    print('  sample rate: %0.6f MHz' % (sdr.rs/1e6))
    print('  center frequency %0.6f MHz' % (sdr.fc/1e6))
    print('  gain: %d dB' % sdr.gain)
    #context = [ad_rdy_ev,rf_q]
    sdr.read_samples_async(rtlsdr_callback, RFSIZE)
    sdr.cancel_read_async()
    sdr.close()
    print('read rtlsdr thread ended')



def audio_callback(in_data, frame_count, time_info, status):
    global audio_q
    return (audio_q.get(),pyaudio.paContinue)

if __name__ == '__main__':
    global sdr

    #processes
    rf_q = queue.Queue()
    audio_q = queue.Queue()
    ad_rdy_ev = threading.Event()

    t_read_data = threading.Thread(target=read_data_thread,args=(rf_q,ad_rdy_ev,audio_q,))
    t_rtlsdr = threading.Thread(target=rtlsdr_thread,args=(rf_q,ad_rdy_ev,))

    t_read_data.daemon=True
    t_read_data.start()
    t_rtlsdr.daemon=True
    t_rtlsdr.start()

    #pyaduio
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

    block = input("Please input sth: \n")
    print(block)

    stream.stop_stream()
    stream.close()