try:
  from gpiozero import Device
  if not Device.pin_factory:
    from gpiozero.pins.mock import MockFactory
    Device.pin_factory = MockFactory()
except ModuleNotFoundError:
  print("ERROR: 'gpiozero' must be installed")
  import sys
  sys.exit(1)

