# -*- coding: utf-8 -*-
"""
从一位前辈处学习来的：
https://github.com/licheegh/dig_sig_py_study/blob/master/RTL_PY/fm_radio.py

学习了解码过程，多线程操作，音频的操作。收获不少东西。

"""

import threading
import queue
import numpy as np
from scipy import fftpack
from scipy import signal
from rtlsdr import *
import pyaudio

RFRATE = 0.25e6                      # RTLSDR的采样率
RFFREQ = 89.7e6                      # RTLSDR中心频率
RFGAIN = 50						     # 增益

DOWN_FACTOR = 10                     #采样率是250k，而音频播放的速率是25k，需要欠采样，每10个数据取一个

RFSIZE = int(1024*10)				     # 每次采的射频数据大小RTLSDR采集
AUDIOSIZE = int(RFSIZE/DOWN_FACTOR)      # 每次生成的音频数据的大小
FORMAT = pyaudio.paInt16                 # 音频的格式：流数据，跟string不一样，没仔细研究
CHANNELS = 1                             # 音频通道，不清楚作用
AUDIORATE = int(RFRATE/DOWN_FACTOR)      # 音频的采样率


def read_data_thread(rf_q,ad_rdy_ev,audio_q):
    pre_data=0                                    #pre_data的作用是，每段数据最后一个值没有做解码，
    print("read data thread start")               #因此要手动把这个解码做掉；不然在每次处理的就会产生一个异常
    while 1:                                      #最终导致声音效果很差或者直接就没声音
        ad_rdy_ev.wait(timeout=1000)
        while not rf_q.empty():
            data=rf_q.get()
 
            xangle = np.angle(data)
            xda = np.diff(xangle)
            xdata = np.insert(xda,0,xangle[0]-pre_data)
            pre_data = xangle[-1]
            xdata = np.unwrap(xdata,np.pi)
            audiodata = signal.decimate(xdata,DOWN_FACTOR,ftype="fir")   #可以直接10个数据取一个，实验了一下，效果差别不大

            audiodata_amp=audiodata*5e3
            snd_data = audiodata_amp.astype(np.dtype('<i2')).tostring()
            audio_q.put(snd_data)
        ad_rdy_ev.clear()

#rtlsdr
def rtlsdr_callback(samples,rtlsdr_obj):             # rtlsdr的回调函数，每次运行rtlsdr的异步读写函数都会调用
	global rf_q										 # 这个函数就是把read_samples_async读到的值放到射频队列中
	global ad_rdy_ev								 # rtlsdr_obj没啥用处，不过这里必须写成这个样子，不然调用会出错
	rf_q.put(samples)
	ad_rdy_ev.set()                                  # event这个是做几个线程同步的

def rtlsdr_thread(rf_q,ad_rdy_ev):                   #rtlsdr采集数据的线程

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



def audio_callback(in_data, frame_count, time_info, status):      # 音频线程，没深究调用运行机制，这样用就能生效
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
    t_rtlsdr.daemon=True                                  #这个是守护进程，当用户进程全部结束，只剩下守护进程时，守护进程也会结束
    t_rtlsdr.start()                                      #这个程序就是用这个机制将RTLSDR停下来的，JAVA中有类似用法

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

    block = input("Please input sth: \n")                     #这里把音频线程阻塞住，让其运行，输入任意字符回车后，整个程序会停止运行
    print(block)

    stream.stop_stream()
    stream.close()