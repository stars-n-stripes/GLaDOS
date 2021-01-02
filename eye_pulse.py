import sounddevice as sd
import soundfile as sf
# import matplotlib.pyplot as plt
import numpy as np
from gpiozero import PWMLED
# from tkgpio import TkCircuit
from math import floor, ceil
from time import sleep
import wave


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

def main():
    loop_to_output = sd.Stream(callback=eye_blink, device=("Loopback: PCM (hw:2,1)","HDMI 1"),dtype="float32",
                        channels=(2,2), samplerate=48000, blocksize=1024)
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


if __name__ == '__main__':
    main()