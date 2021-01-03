import sounddevice as sd
import soundfile as sf
# import matplotlib.pyplot as plt
import numpy as np
from gpiozero import PWMLED
# from tkgpio import TkCircuit
from math import floor, ceil
from time import sleep
import wave
import threading
from sys import argv
import asyncio
from functools import partial
import sys
import queue


# Copied with awe from https://github.com/scottlawsonbc/audio-reactive-led-strip/blob/master/python/dsp.py
# A+
class ExpFilter:
    """Simple exponential smoothing filter"""
    def __init__(self, val=0.0, alpha_decay=0.5, alpha_rise=0.5):
        """Small rise / decay factors = more smoothing"""
        assert 0.0 < alpha_decay < 1.0, 'Invalid decay smoothing factor'
        assert 0.0 < alpha_rise < 1.0, 'Invalid rise smoothing factor'
        self.alpha_decay = alpha_decay
        self.alpha_rise = alpha_rise
        self.value = val

    def update(self, value):
        if isinstance(self.value, (list, np.ndarray, tuple)):
            alpha = value - self.value
            alpha[alpha > 0.0] = self.alpha_rise
            alpha[alpha <= 0.0] = self.alpha_decay
        else:
            alpha = self.alpha_rise if value > self.value else self.alpha_decay
        self.value = alpha * value + (1.0 - alpha) * self.value
        self.value = max(self.value, 0.25) # Bind value within [0,1]
        return min(self.value, 1) # So we don't error out the LED





# https://stackoverflow.com/questions/40138031/how-to-read-realtime-microphone-audio-volume-in-python-and-ffmpeg-or-similar

output = []
# TODO: Change to config.ini
EYE = PWMLED(17)
BLOCKSIZE = 1024
LAST_PWM = 0
EYE_LEVEL = ExpFilter(val=0.5)
BT_DELAY = 0.5

async def pwm_updater(pwm_value, delay):
    """Set the PWMLED pin after waiting a small amount of time

    Args:
        pwm_value (float): new PWM value within the bounds [0.0, 1.0]
        delay (float): Delay, in seconds, before setting the GPIO pin
    """
    global EYE
    await asyncio.sleep(delay)
    EYE.value = pwm_value

# Oodles of asynchronous examples from sd docs:
# https://python-sounddevice.readthedocs.io/en/0.4.1/examples.html#creating-an-asyncio-generator-for-audio-blocks

async def inputstream_generator(channels=1, **kwargs):
    """Generator that yields blocks of input data as NumPy arrays."""
    q_in = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def callback(indata, frame_count, time_info, status):
        loop.call_soon_threadsafe(q_in.put_nowait, (indata.copy(), status))

    stream = sd.InputStream(callback=callback, channels=channels, **kwargs)
    with stream:
        while True:
            indata, status = await q_in.get()
            yield indata, status


async def stream_generator(blocksize, *, channels=1, dtype='float32',
                           pre_fill_blocks=10, **kwargs):
    """Generator that yields blocks of input/output data as NumPy arrays.

    The output blocks are uninitialized and have to be filled with
    appropriate audio signals.

    """
    assert blocksize != 0
    q_in = asyncio.Queue()
    q_out = queue.Queue()
    loop = asyncio.get_event_loop()

    def callback(indata, outdata, frame_count, time_info, status):
        loop.call_soon_threadsafe(q_in.put_nowait, (indata.copy(), status))
        outdata[:] = q_out.get_nowait()

    # pre-fill output queue
    for _ in range(pre_fill_blocks):
        q_out.put(np.zeros((blocksize, channels), dtype=dtype))

    stream = sd.Stream(blocksize=blocksize, callback=callback, dtype=dtype,
                       channels=channels, **kwargs)
    with stream:
        while True:
            indata, status = await q_in.get()
            outdata = np.empty((blocksize, channels), dtype=dtype)
            yield indata, outdata, status
            q_out.put_nowait(outdata)


# async def print_input_infos(**kwargs):
#     """Show minimum and maximum value of each incoming audio block."""
#     async for indata, status in inputstream_generator(**kwargs):
#         if status:
#             print(status)
#         print('min:', indata.min(), '\t', 'max:', indata.max())


async def wire_coro(delay=0.5, **kwargs):
    """Create a connection between audio inputs and outputs.

    Asynchronously iterates over a stream generator and for each block
    simply copies the input data into the output block.

    """
    async for indata, outdata, status in stream_generator(**kwargs):
        if status:
            print(status)

        # Extract the expected value and send it to the delayed GPIO pin
        out = np.linalg.norm(indata) / 10
        pwm_value = EYE_LEVEL.update(out)
        asyncio.create_task(pwm_updater(pwm_value, delay))

        outdata[:] = indata


def print_sound(indata, outdata, frames, time, status):
    # volume_norm = np.linalg.norm(indata)
    out = np.linalg.norm(indata) / 10
    # test = indata / np.max(indata)
    # print(np.median(test))
    # print(out)
    output.append(out)
    # print(out)
    pwm_value = round(min(0.25 + out, 1), 2)
    print(pwm_value, ": ", "|"*floor(pwm_value * 10))
    outdata[:] = indata




def eye_blink(indata, outdata, frames, time, status):
    global EYE, EYE_LEVEL
    out = np.linalg.norm(indata) / 10

    # Send the audio on to our output sink
    outdata[:] = indata

    # print(pwm_value)
    # Update the LED
    pwm_value = EYE_LEVEL.update(out)
    EYE.value = pwm_value




def eye_blink_bt(indata, outdata, frames, time, status, queue, delay):
    global EYE, EYE_LEVEL
    out = np.linalg.norm(indata) / 10

    # Send the audio on to our output sink
    outdata[:] = indata

    # print(pwm_value)
    # Enqueue a new LED value to the gpio worker
    pwm_value = EYE_LEVEL.update(out)
    print("placing into queue...")
    queue.put_nowait((pwm_value, delay))
    


def eye_blink_listen(indata, frames, time, status):
    global EYE, EYE_LEVEL
    out = np.linalg.norm(indata) / 10
    print(out)
    # print(pwm_value)
    # Update the LED
    pwm_value = EYE_LEVEL.update(out)
    EYE.value = pwm_value


def eye_blink_nofilter(indata, outdata, frames, time, status):
    global LAST_PWM
    # volume_norm = np.linalg.norm(indata)
    out = np.linalg.norm(indata) / 10
    # test = indata / np.max(indata)
    # print(np.median(test))
    # print(out)
    output.append(out) # for debugging with matplotlib
    # print(out)
    pwm_value = round(min(0.10 + out, 1), 2)
    # print(pwm_value, ": ", "|"*floor(pwm_value * 10))

    # Fill the buffer if it's short
    # if len(indata) < BLOCKSIZE:
    #     outdata[:len(indata)] = indata
    #     outdata[len(indata):] = b'\x00' * (len(outdata) - len(indata))
    # else:
    #     outdata[:] = indata
    outdata[:] = indata
    # Light the eye, but on the next callback
    # EYE.value = LAST_PWM
    # LAST_PWM = pwm_value
    EYE.value = pwm_value
    # DEBUG: print latency

def play_file():
    loop_to_output = sd.Stream(callback=eye_blink, device=("Loopback: PCM (hw:2,1)","HDMI 1"),dtype="float32",
                        channels=(2,2), samplerate=48000, blocksize=1024)
    loop_to_output.start()
    with loop_to_output:
        # sd.play("test.wav", device=8, dtype="float32")

        data, fs = sf.read("test.wav", dtype='float32')

        # Give loop_to_output a chance to connect the loopback to HDMI
        # Otherwise, the start of the .wav file gets cut off.
        sd.sleep(250)
        sd.play(data, fs, device="Loopback: PCM (hw:2,0)")

        # TODO: Why the extra second? Figure out how to not rely on the "+1000", as I feel like that's contingent on the latency
        sd.sleep(ceil(len(data) / fs * 1000))
        # wait for OS to complete, not the play statement above
        # sd.wait()
        
        # while not sd.wait():
            # print(os.latency)

        # plt.plot(output)
        # plt.show()
        # with sd.OutputStream(callback=print_sound, device=6,
        #                 dtype="float32",
        #                 channels=(2,2), samplerate=48000, blocksize=2048):
        # # sd.play("test.wav", device=8, dtype="float32")

        #     data, fs = sf.read("test.wav", dtype='float32')

        #     sd.play(data, fs, device=6)
        #     status = sd.wait()
async def main():
    """If this is called with main, listen forever on the given device, forwarding all data to a virtual input
    """

    #TODO: replace with ArgParse
    if argv[1] == "bt":
             audio_delay = BT_DELAY
    else:
        audio_delay = 0

    audio_task = asyncio.create_task(wire_coro(delay=audio_delay, device=("Loopback ,0)","googlehome"),dtype="float32",
                        channels=2, samplerate=48000, blocksize=1024))
    # Or...
    # audio_task = asyncio.create_task(wire_coro(**kwargs))
    try:
        while True:
            await asyncio.sleep(1)

    except asyncio.CancelledError:
        print('\nwire was cancelled')
    except KeyboardInterrupt:
        print("Shutting down stream...")
        audio_task.cancel()
        try:
            await audio_task
        except asyncio.CancelledError:
            print("Shutdown stream. Goodbye!")
            sys.exit(0)
        
        
    # else:
    #     print("Creating HDMI Stream...")
    #     loop_to_output = sd.Stream(callback=eye_blink, device=("Loopback ,0)","HDMI"),dtype="float32",
    #                         channels=(2,2), samplerate=48000, blocksize=1024)
    #     loop_to_output.start()
    #     with loop_to_output:        
    #         print("Starting Stream")
    #         while True:
    #             # sleep(1000)
    #             pass

if __name__ == '__main__':
    asyncio.run(main())