## Dependencies

* pygpio
* python evdev
* being in the gpio group

## Loading hardware objects

There's a basic launcher script, e.g. `two_button.py`.  This script should only contain the business logic, and high level interface.

Hardware itself is enabled through the ini file.  For example:

    [pins]
    on_button = Button:11:38

This enables the code in the launcher script to load some number of devices to use as an enabling button (the name is arbitrary):

    class Dispatcher(BaseDispatcher):
      def __init__(self, config):
        super(Dispatcher, self).__init__(config)
        ...
        self.load_config_object('on_button', on_down=self.on_button_down)

Then whenever necessary, you can call

    self.on_button.blink()
    # or
    self.on_button.off()

to change its light, or in

    def on_button_down(self, source):
      print "Button pressed"

## Multiple hardware for one action

Simple! It's a list.

    [pins]
    enable_output = Relay:ActiveHigh:29
    # or
    enable_output = Relay:ActiveHigh:29, Relay:ActiveHigh:31
    

## Threading model

Each hardware device (button, buzzer, etc) may start its own thread, but events are delivered in one main thread for ease of programming.

## Running on boot

The simplest way is adding an `@reboot cd /path/to/source; python two_button.py` to `crontab -e`.  You can also make a systemd unit, if your distro supports that.

## More reading

See `qa.py` or `two_button.py` for examples of how this can be used.