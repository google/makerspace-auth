# Pi Hat 1

This is an example board that fits a Raspberry Pi.  We tried to make it fun
enough to assemble as a beginning soldering exercise (yes, even with surface
mount!), and not use anything too strange.

![Board image](board.png)

## Part notes

The odd board shape is to preserve easy access to CSI bus in case you're using
a camera.

We tested with 2x20 headers both cheap (eBay) and expensive
(SFH11-PBPC-D20-ST-BK at $1.97).  All fit, barely clearing the holes.

The top hole is intended as mechanical joining, but as in all Pi hats, needs an
odd size standoff (M2.5 x 11mm).

You don't need both the 2-pin and barrely supply (in fact, don't power both
simultaneously), but having the second set of pads makes probing easier.

The resistor network can be bussed or independent, either will work.  10k
appears sufficient to overpower the onboard pulldown on boot, but 4.7k (less
common) works too.


## Pinouts

The button pinout is (left-to-right with the tab facing down) is (``IN, n/c,
GND, +12V, Switched GND``).  It's intended for a light and/or button per
connector.  Arcade buttons work fairly well if your enclosure is big enough.

![Button image](buttonwiring.jpg)

The only connector with freewheeling diode is the one marked high current.  It's
intended for relay or solenoid use, like for a door.  It's fairly easy to blow
the driver chip on all the others if using an inductive load (from experience).
