# Software
## Version 0.1

The current iteration listens for an RFID badge scan event, which starts the "on" (red) button blinking and waits for a press event. Once red is pressed, the light becomes solid and a connected power switch comes on (turning on a device). If, at any point after a successful badge scan, the "off" (blue) button is pressed, the program resets to waiting for a badge scan (turning off LEDs and connected power switch).

## Custom Variables

Depending on the badge reader used, a name will need provided to
"get_scanner_device()" in main.py. To find the names of connected devices, `findKeyboards.py` can be run.
