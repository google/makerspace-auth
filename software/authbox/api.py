# Copyright 2017-2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Main API for Authbox.

Your business logic should subclass BaseDispatcher and set up your peripherals
in its __init__ method.  Most simple uses will use callbacks for everything.
See two_button.py as an example workflow.

Peripherals are kept in other files in this same package, and should be listed
in CLASS_REGISTRY so they can be loaded lazily.
"""

from __future__ import print_function

import sys
import threading
import traceback
import types

from authbox.compat import queue
from RPi import GPIO

# The line above simplifies imports for other modules that are already importing from api.

# TODO give each object a logger and use that instead of prints


CLASS_REGISTRY = [
    "authbox.badgereader_hid_keystroking.HIDKeystrokingReader",
    "authbox.badgereader_wiegand_gpio.WiegandGPIOReader",
    "authbox.gpio_button.Button",
    "authbox.gpio_relay.Relay",
    "authbox.gpio_buzzer.Buzzer",
    "authbox.timer.Timer",
]

# Add this to event_queue to request a graceful shutdown.
SHUTDOWN_SENTINEL = object()


class BaseDispatcher(object):
    def __init__(self, config):
        self.config = config
        self.event_queue = queue.Queue()  # unbounded
        self.threads = []

    def load_config_object(self, name, **kwargs):
        # N.b. args are from config, kwargs are passed from python.
        # This sometimes causes confusing error messages like
        # "takes at least 5 arguments (5 given)".
        config_items = split_escaped(self.config.get("pins", name), preserve=True)
        objs = []
        for item in config_items:
            options = list(split_escaped(item.strip(), glue=":"))
            cls_name = options[0]
            for c in CLASS_REGISTRY:
                if c.endswith("." + cls_name):
                    cls = _import(c)
                    break
            else:
                # This is a Python for-else, which executes if the body above didn't
                # execute 'break'.
                raise Exception("Unknown item", name)
            print("Instantiating", cls, self.event_queue, name, options[1:], kwargs)
            obj = cls(self.event_queue, name, *options[1:], **kwargs)
            objs.append(obj)
            self.threads.append(obj)
        if len(objs) == 1:
            setattr(self, name, obj)
        else:
            setattr(self, name, MultiProxy(objs))

    def run_loop(self):
        # Doesn't really support calling run_loop() more than once
        for th in self.threads:
            th.start()
        try:
            while True:
                # We pass a small timeout because .get(block=True) without it causes
                # trouble handling Ctrl-C.
                try:
                    item = self.event_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                if item is SHUTDOWN_SENTINEL:
                    break
                # These only happen here to serialize access regardless of what thread
                # handled it.
                func, args = item[0], item[1:]
                try:
                    func(*args)
                except Exception as e:
                    traceback.print_exc()
                    print("Got exception", repr(e), "executing", func, args)
        except KeyboardInterrupt:
            print("Got Ctrl-C, shutting down.")

        # Assuming all threads are daemonized, we will now shut down.


class BaseDerivedThread(threading.Thread):
    def __init__(self, event_queue, config_name):
        # TODO should they also have numeric ids?
        thread_name = "%s %s" % (self.__class__.__name__, config_name)
        super(BaseDerivedThread, self).__init__(name=thread_name)
        self.daemon = True

        self.event_queue = event_queue
        self.config_name = config_name

    def run(self):
        while True:
            try:
                self.run_inner()
            except Exception:
                traceback.print_exc()


class BasePinThread(BaseDerivedThread):
    def __init__(
        self, event_queue, config_name, input_pin, output_pin, initial_output=GPIO.LOW
    ):
        super(BasePinThread, self).__init__(event_queue, config_name)

        self.input_pin = input_pin
        self.output_pin = output_pin

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)  # for reusing pins
        if self.input_pin:
            GPIO.setup(self.input_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        if self.output_pin:
            GPIO.setup(self.output_pin, GPIO.OUT, initial=initial_output)


class BaseWiegandPinThread(BaseDerivedThread):
    def __init__(self, event_queue, config_name, d0_pin, d1_pin):
        super(BaseWiegandPinThread, self).__init__(event_queue, config_name)

        self.d0_pin = d0_pin
        self.d1_pin = d1_pin

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)  # for reusing pins
        if self.d0_pin:
            GPIO.setup(self.d0_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        if self.d1_pin:
            GPIO.setup(self.d1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


class NoMatchingDevice(Exception):
    """Generic exception for missing devices."""


def _import(name):
    module, object_name = name.rsplit(".", 1)
    # The return value of __import__ requires walking the dots, so
    # this is a fairly standard workaround that's easier.  Intermediate
    # names appear to always get added to sys.modules.
    __import__(module)
    return getattr(sys.modules[module], object_name)


class MultiMethodProxy(object):
    def __init__(self, objs, meth):
        self.objs = objs
        self.meth = meth

    def __call__(self, *args, **kwargs):
        for i in self.objs:
            getattr(i, self.meth)(*args, **kwargs)


class MultiProxy(object):
    def __init__(self, objs):
        self.objs = objs

    def __getattr__(self, name):
        if isinstance(getattr(self.objs[0], name), types.MethodType):
            return MultiMethodProxy(self.objs, name)
        else:
            return getattr(self.objs[0], name)


def split_escaped(s, glue=",", preserve=False):
    """Handle single-char escapes using backslash."""
    buf = []
    it = iter(s)
    for c in it:
        if c == glue:
            yield "".join(buf)
            del buf[:]
        elif c == "\\":
            if preserve:
                buf.append(c)
            c = next(it)
            buf.append(c)
        else:
            buf.append(c)
    if buf:
        yield "".join(buf)
