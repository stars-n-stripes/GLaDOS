#!/bin/bash

# TODO: Any ALSA changes we need to do beforehand

# Connect to bluetooth
bt_info=$(bluetoothctl info)
if ! echo "$bt_info" | grep -q "$GHOME_ADDR"; then
	# BT is not connected; try to connect
	# Fun fact, $? does become the return value of bluetoothctl since btc_out doesn't have
	# a return value itself.
	btc_out=$(bluetoothctl connect "$GHOME_ADDR")
	if ! $?; then
		# there was an error
		echo "ERROR: Failed to connect to Bluetooth Speaker at $GHOME_ADDR. Exiting."
		exit 1
	fi
fi

# Start script that turns on mycroft (won't block)
mycroft-start all
if ! $?; then
	# Mycroft failed, somehow
	echo "ERROR: Mycroft failed to start. Exiting"
	exit 1
fi

# Run the eyepulse listener in the backgroun
python3 /code/GLaDOS/eye_pulse.py bt &

# Report completion
echo "GLaDOS is booted and ready. PID of eye pulse stream is $!"
