import sounddevice as sd
import soundfile as sf
# import matplotlib.pyplot as plt
import numpy as np
from gpiozero import PWMLED
# from tkgpio import TkCircuit
from math import floor, ceil
from time import sleep
import wave

# https://stackoverflow.com/questions/40138031/how-to-read-realtime-microphone-audio-volume-in-python-and-ffmpeg-or-similar

output = []
# TODO: Change to config.ini
EYE = PWMLED(17)
BLOCKSIZE = 1024
LAST_PWM = 0

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
    global LAST_PWM
    # volume_norm = np.linalg.norm(indata)
    out = np.linalg.norm(indata) / 10
    # test = indata / np.max(indata)
    # print(np.median(test))
    # print(out)
    output.append(out)
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

    with sd.Stream(callback=eye_blink, device=("Loopback: PCM (hw:2,1)","default"),dtype="float32",
                        channels=(2,2), samplerate=41400) as os:
        # sd.play("test.wav", device=8, dtype="float32")

        data, fs = sf.read("test.wav", dtype='float32')

        sd.play(data, fs, device="Loopback: PCM (hw:2,0)")

        # TODO: Why the extra second? Figure out how to not rely on the "+1000", as I feel like that's contingent on the latency
        sd.sleep(ceil(len(data) / fs * 1000) + 1000 + 700)
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