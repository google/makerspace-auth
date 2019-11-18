# Software

For the basic walkthrough of how this code works, see https://google.github.io/makerspace-auth/client/Walkthrough.html

Prerequisites:

1. Python 2.7 or 3.6+
1. `evdev` (python-evdev on Debian)
1. `RPi` module (or `pip install fake-rpi` for testing)
1. Make sure you're in the 'input' group to use evdev
1. Make sure you're in the gpio group if you're on a Pi

Developing:

1. The easiest way is to run `make setup` and then `. .venv/bin/activate`.
1. You can also run the tests with tox, using `tox -p all`
1. The code is formatted with isort+black, run `make lint` and/or `make format`
   before sending pull requests.


## Protocol

While using a server is optional (you can do everything with shell scripts), we
use a simple HTTP-based protocol that's intended to be easy to adapt to existing
systems. See https://google.github.io/makerspace-auth/server/Protocol.html


## QA example

This simply flashes a light when its button is pressed.  We use this to run QA
on authboards once assembled, and is a very simple example of how the event loop
works.


## Two-button example

We determined two buttons ("on" and "off", basically) to be the minimum viable
controls, and this is the version that we use at Google.  If you're looking for
a good jumping-off point, start here.

The basic workflow is:

1. Scan badge
1. Press "on".  Tool will power up.
1. Warning timer commences beeps.  If you press "on" again, you get more time.
1. Otherwise, tool powers off.

You should copy (or symlink) this file to ~/.authboxrc and make edits to conform
to your pin numbers.  The defaults are for an RDR-6081AKU (keystroking) and
pi-hat-1 v1.0 hardware triggering both onbarod relays to enable devices.

This example out of the box stores authorized users in a local file
(See `sample_auth_check.sh`) but you likely want it to query your existing
user/training database.  If you'd like to use the same protocol, that's
documented at
https://google.github.io/makerspace-auth/server/Protocol.html and if you use
curl, remember the '-f'.

## Starting on boot

The simplest way that works on all distros is a cron job:

    # Visually
    pi$ crontab -e
    (add the following line at the end, save, and apply)
    @reboot cd /path/to/software; python two_button.py

    # Through script
    pi$ (crontab -l; echo "@reboot cd /path/to/software; python two_button.py") | crontab -

If your distro uses systemd, you can also make a systemd unit that runs it.
