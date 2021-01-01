from tkgpio import TkCircuit

# initialize the circuit inside the 

configuration = {
    "width": 100,
    "height": 100,
    "leds": [
        {"x": 33, "y": 40, "name": "EYE", "pin": 21}
    ]
    # "buttons": [
    #     {"x": 50, "y": 130, "name": "Press to toggle LED 2", "pin": 11},
    # ]
}

circuit = TkCircuit(configuration)


@circuit.run
def main():
    # now just write the code you would use on a real Raspberry Pi

    from gpiozero import LED, Button, PWMLED
    from time import sleep

    led1 = PWMLED(21)
    for x in range(11):
        led1.value = x/10
        sleep(0.5)
