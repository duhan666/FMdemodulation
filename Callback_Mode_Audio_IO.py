"""PyAudio Example: Play a wave file (callback version).

In callback mode, PyAudio will call a specified callback function (2) whenever it needs new audio data (to play) and/or when there is new (recorded) audio data available. Note that PyAudio calls the callback function in a separate thread. The function has the following signature callback(<input_data>, <frame_count>, <time_info>, <status_flag>) and must return a tuple containing frame_count frames of audio data and a flag signifying whether there are more frames to play/record.

Start processing the audio stream using pyaudio.Stream.start_stream() (4), which will call the callback function repeatedly until that function returns pyaudio.paComplete.

To keep the stream active, the main thread must not terminate, e.g., by sleeping (5).


"""

import pyaudio
import wave
import time
import sys



wf = wave.open(r'wavsamp.wav', 'rb')

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

# define callback (2)
def callback(in_data, frame_count, time_info, status):
    data = wf.readframes(frame_count)
    return (data, pyaudio.paContinue)

# open stream using callback (3)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=callback)

# start the stream (4)
stream.start_stream()

# wait for stream to finish (5)
while stream.is_active():
    time.sleep(0.1)

# stop stream (6)
stream.stop_stream()
stream.close()
wf.close()

# close PyAudio (7)
p.terminate()