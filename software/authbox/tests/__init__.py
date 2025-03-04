__version__ = "1.0.0"

try:
  from gpiozero import Device
  from gpiozero.pins.mock import MockFactory
  Device.pin_factory = MockFactory()
except ModuleNotFoundError:
  print("ERROR: 'gpiozero' must be installed")
  import sys
  sys.exit(1)

