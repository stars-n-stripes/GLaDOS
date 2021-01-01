#!/usr/bin/env python3
"""Play an audio file using a limited amount of memory.

The soundfile module (https://PySoundFile.readthedocs.io/) must be
installed for this to work.  NumPy is not needed.

In contrast to play_file.py, which loads the whole file into memory
before starting playback, this example program only holds a given number
of audio blocks in memory and is therefore able to play files that are
larger than the available RAM.

A similar example could of course be implemented using NumPy,
but this example shows what can be done when NumPy is not available.

"""
import argparse
import queue
import sys
import threading
import wave
import audioop
import math
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd

import sounddevice as sd
import soundfile as sf


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

with wave.Wave_read("test.wav") as wavefile:
    samplewidth = wavefile.getsampwidth()
    channels = wavefile.getnchannels()
    # exit(0)


# strip out the argparse block and hardcode defaults for debug
# blocksize = sd.default.blocksize
blocksize = 64
print(blocksize)
buffersize = 1024
device = sd.default.device
filename = "test.wav"
q = queue.Queue(maxsize=buffersize)
event = threading.Event()


def db_level(sampwidth, channels, frames):
    """
    Returns the average audio volume level measured in dB (range -60 db to 0 db)
    If the sample is stereo, you get back a tuple: (left_level, right_level)
    If the sample is mono, you still get a tuple but both values will be the same.
    This method is probably only useful if processed on very short sample fragments in sequence,
    so the db levels could be used to show a level meter for the duration of the sample.
    """
    maxvalue = 2 ** (8 * sampwidth- 1)
    if channels == 1:
        peak_left = peak_right = (audioop.max(frames, sampwidth) + 1) / maxvalue
    else:
        left_frames = audioop.tomono(frames, sampwidth, 1, 0)
        right_frames = audioop.tomono(frames, sampwidth, 0, 1)

        peak_left = (audioop.max(left_frames, sampwidth) + 1) / maxvalue
        peak_right = (audioop.max(right_frames, sampwidth) + 1) / maxvalue
    # cut off at the bottom at -60 instead of all the way down to -infinity
    return max(20.0*math.log(peak_left, 10), -60.0), max(20.0*math.log(peak_right, 10), -60.0)

def callback(outdata, frames, time, status):
    # print(frames, "/", blocksize)
    # assert frames == blocksize
    if status.output_underflow:
        print('Output underflow: increase blocksize?', file=sys.stderr)
        raise sd.CallbackAbort
    assert not status
    try:
        data = q.get_nowait()
    except queue.Empty as e:
        print('Buffer is empty: increase buffersize?', file=sys.stderr)
        raise sd.CallbackAbort from e
    if len(data) < len(outdata):
        outdata[:len(data)] = data
        outdata[len(data):] = b'\x00' * (len(outdata) - len(data))
        raise sd.CallbackStop
    else:
        outdata[:] = data


try:
    dbs = []
    with sf.SoundFile(filename) as f:

        for _ in range(buffersize):
            data = f.buffer_read(blocksize, dtype='float32')
            dbs.append(db_level(samplewidth, channels, data))

            if not data:
                break
            q.put_nowait(data)  # Pre-fill queue
        stream = sd.RawOutputStream(
            samplerate=f.samplerate, blocksize=blocksize,
            device=device, channels=f.channels, dtype='float32',
            callback=callback, finished_callback=event.set)
        with stream:
            timeout = blocksize * buffersize / f.samplerate
            while data:
                data = f.buffer_read(blocksize, dtype='float32')
                q.put(data, timeout=timeout)
            event.wait()  # Wait until playback is finished
except KeyboardInterrupt:
    exit('\nInterrupted by user')
except queue.Full:
    # A timeout occurred, i.e. there was an error in the callback
    exit(1)
except Exception as e:
    raise e

plt.plot([x[1] for x in dbs])
plt.ylabel("right channel vol")
plt.show()
