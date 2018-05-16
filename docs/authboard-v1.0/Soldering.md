## General Assembly

This involves a good amount of SMT soldering.  If you've never done it before, watch [this video](https://www.youtube.com/watch?v=_kNTFCuy4xk) I threw together.  The first rule I'll give you with is that any pin can take 2 seconds of heat without damage at normal temperatures (up to 700 deg F).  More than that is at your own risk.  The second is that generally the numbers on these parts face up.

The parts that might burn out due to overcurrent are on the bottom of the board -- worse for automated assembly, much better for replacing after a failure.  I'd suggest roughly this order of assembly:

* R1, LED1 (touch with a bench supply to GND, 12V and confirm light)
* R2, LED2 (touch with a bench supply to GND, OUT and confirm light)
* D1, D2, C2 

Take a break.  You're done with the top-side 2-pin SMT.

* R3-R6 (bottom side)
* IC1, bottom side observing polarity (for the most clearance, this is first).
* Q1-Q6, bottom side
* JP1 (40-pin header, which is inserted from bottom side and soldered on top). No keying on the Raspbery Pi GPIOs so it doesn't matter which way you place this.

Take another break.

* J11 (buck module) with ADJ trace cut and 5V solder jumper closed.  Install and test without a Pi, and with a bench supply at 12V: You should get 5V on output and not hit a 100mA current limit.
* Remaining J connectors, being careful that they are installed straight.
