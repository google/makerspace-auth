# Startup Script

## About

In this directory is a Systemd [Service][systemd.service] Unit focused on the
setup running of the Makerspace Auth code on the Raspberry Pi.

## Installation

After configuration (see below) this script should be placed in
`/etc/systemd/system` named `makerspace-auth.service`.

If, after creating the file at that location, changes are desired the user will
need to reload the file (`systemctl daemon-reload`) to refresh any relevant
changes.

After copying the file to `/etc/systemd/system` it can be started by running:

```
systemctl start makerspace-auth
```

It can also be set to automatically start on boot by running:

```
systemctl enable makerspace-auth
```

Fore more information read the [systemd] documentation.

## Configuration

For most users there is only a single option which will need to be changed:
the name of the script to be called on the `ExecStart` line.  In this example it
calls the `doorauth.py` script located in the `/software` subdirectory of the
repository.


The other options in the script handle the following:


| option | purpose |
| --- | --- |
| Type=simple | Expect the unit to run in the foreground, allowing systemd to directly detect if the unit has stopped (and then restart it) |
| ExecStart=/usr/bin/python doorauth.py | Fully qualified path to be executed |
| WorkingDirectory=/home/pi/makerspace-auth/software | Use this path as the working directory when running the unit |
| User=pi | Run the unit as the `pi` user |
| Group=pi | Run the unit as the `pi` group |
| Restart=always | Always attempt to restart the unit if it stops (except when stopped by an administrator with `systemctl` |
| RestartSec=2s | Insert a 2 second delay in between restart attempts |
| Environment=PYTHONUNBUFFERED=true | Do not buffer output, instead immediately flush it to the journal  |
| NoNewPrivileges=true | Do not allow our unit to gain new privileges via SETUID, SETUID, or other filesystem capabilities |
| ProtectSystem=full | Ensure that `/usr`, `/lib`, and `/etc/` are seen as read-only by our unit |
| RestrictRealtime=true | Do not allow the process to change it's kernel scheduling to realtime mode |
| StandardOutput=journal | Ensure all output from `STDOUT` ends up in the systemd journal |
| StandardError=journal | Ensure all output from `STDERR` ends up in the systemd journal |




[systemd.service]: https://www.freedesktop.org/software/systemd/man/systemd.service.html
[systemd]: https://www.freedesktop.org/wiki/Software/systemd/
