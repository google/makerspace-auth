# Software

## Two-button example

See `two_button.py` for an example of how to incorporate your business logic.

The basic workflow is:

1. Scan badge
1. Press "on".  Tool will power up.
1. Warning timer commences beeps.  If you press "on" again, you get more time.
1. Otherwise, tool powers off.

You should copy (or symlink) this file to ~/.authboxrc and make edits to conform
to your pin numbers.  The defaults are for an RDR-6081AKU (keystroking) and
pi-hat-1 v0.3 hardware with a relay (or PowerSwitch Tail) on the high power port.

To start on boot, look into creating either a systemd unit or @reboot cron
entry.
