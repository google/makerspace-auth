#!/usr/bin/python

# finds keyboards connected to system
import evdev

def main():
	print("Input devices connected to machine:")
	devices = [evdev.InputDevice(x) for x in evdev.list_devices()]
	for i in devices:
		print devices[devices.index(i)]

if __name__ == "__main__":
	main()