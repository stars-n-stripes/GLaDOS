#!/bin/bash

# TODO: Any ALSA changes we need to do beforehand

# Start script that turns on mycroft
mycroft-start all

# Run the eyepulse listener
python3 /code/GLaDOS/eye_pulse.py
