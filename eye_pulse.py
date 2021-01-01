import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
import numpy as np
from gpiozero import PWMLED
# from tkgpio import TkCircuit
from math import floor



output = []

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

def main():

    with sd.Stream(callback=print_sound, device=(2,5),
                        dtype="float32",
                        channels=(2,2), samplerate=44100):
        # sd.play("test.wav", device=8, dtype="float32")

        data, fs = sf.read("test.wav", dtype='float32')

        sd.play(data, fs, device=8)
        status = sd.wait()

        plt.plot(output)
        plt.show()



if __name__ == '__main__':
    main()