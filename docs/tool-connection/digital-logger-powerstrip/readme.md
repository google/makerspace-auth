In order to add support for the Digital Loggers IoT relay (https://www.digital-loggers.com/iotfaqs.html), make the following changes:

1: Attach the positive lead to pin 1 of J7 (the pin closest to the J12/J13 relays) and the negative lead to J7 pin 2.

2: Update the two_button.ini config so that line 39 now reads " enable_output = Relay:ActiveHigh:40 ".

3: Verify pins 1 and 2 alternate from 12v to 0v with a multimeter, as you actuate the buttons.



Note: Other ports may be workable as well, depending on what you have attached to your hat. Look at hardware/pi-hat-1/ms_auth_breakout.pdf for the full trace. 
J7 is the simplest (the high current relay, ~1A at 12V), but J1-5 may be workable as well (using pin 4 and pin 1 for BN_Logic as a relay). This is untested.
In a pinch, J8 may also work if you're not using an RGB light. 

Note that J12/13 do not work, as they are the volt free switches and the IoT relay expects a 3-60V DC signal.

Also note that polarity matters, so be sure you're sending +12V to the IoT relay.
