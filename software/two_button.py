#!/usr/bin/python
#
# Copyright 2017 Google Inc. All Rights Reserved.
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

"""Example using two buttons for "on" and "off" once badged.

"""
from __future__ import print_function

import os
import shlex
import subprocess
import sys

from authbox.api import BaseDispatcher, MultiProxy, split_escaped
from authbox.config import Config
from authbox.timer import Timer

DEVNULL = open("/dev/null", "r+")


class Dispatcher(BaseDispatcher):
    def __init__(self, config):
        super(Dispatcher, self).__init__(config)

        self.authorized = False
        self.load_config_object("on_button", on_down=self.on_button_down)
        self.load_config_object("off_button", on_down=self.abort)
        self.load_config_object("badge_reader", on_scan=self.badge_scan)
        self.load_config_object("enable_output")
        self.load_config_object("buzzer")

        # Custom loading for enable_output to support delay
        enable_outputs_config = list(
            split_escaped(self.config.get("pins", "enable_output"), preserve=True)
        )

        self.delay_map = self._load_delay_map()

        self.outputs = []
        if isinstance(self.enable_output, MultiProxy):
            objs = self.enable_output.objs
        else:
            objs = [self.enable_output]

        for i, obj in enumerate(objs):
            if i < len(enable_outputs_config):
                pin_str = enable_outputs_config[i].strip()
                delay = self.delay_map.get(pin_str, 0)
                self.outputs.append((obj, delay))
            else:
                self.outputs.append((obj, 0))

        self.warning_timer = Timer(self.event_queue, "warning_timer", self.warning)
        self.expire_timer = Timer(self.event_queue, "expire_timer", self.abort)
        self.expecting_press_timer = Timer(
            self.event_queue, "expecting_press_timer", self.abort
        )

        self.timers = {}
        self.threads.extend(
            [self.warning_timer, self.expire_timer, self.expecting_press_timer]
        )

        for obj, delay in self.outputs:
            if delay > 0:
                timer_name = f"off_timer_{id(obj)}"
                # Lambda captures obj correctly if we use a default arg.
                timer = Timer(
                    self.event_queue,
                    timer_name,
                    lambda source, o=obj: self.delayed_off_generic(o),
                )
                self.timers[id(obj)] = (timer, delay)
                self.threads.append(timer)

        self.noise = None
        self.delayed_off_running = False
        self.running_timers_count = 0

    def _get_command_line(self, section, key, format_args):
        """Constructs a command line, safely.

        The value can contain {key}, {}, and {5} style interpolation:
          - {key} will be resolved in the config.get; those are considered safe and
            spaces will separate args.
          - {} works on each arg independently (probably not what you want).
          - {5} works fine.
        """
        value = self.config.get(section, key)
        pieces = shlex.split(value)
        return [p.format(*format_args) for p in pieces]

    def _load_delay_map(self):
        delay_map = {}
        try:
            delays_str = self.config.get("pins", "output_off_delay_seconds")
            delay_map = self._parse_delay_str(delays_str)
        except Exception:
            pass

        if not delay_map:
            try:
                delays_str = self.config.get("auth", "output_off_delay_seconds")
                delay_map = self._parse_delay_str(delays_str)
            except Exception:
                pass

        return delay_map

    def _parse_delay_str(self, delays_str):
        delay_map = {}
        if not delays_str:
            return delay_map
        delays_str = delays_str.replace("[", "").replace("]", "").strip()
        pairs = [p.strip() for p in delays_str.split(",")]
        for pair in pairs:
            if "=" in pair:
                k, v = pair.split("=")
                k = k.strip()
                v = v.strip()
                try:
                    # Use Config.parse_time to support suffixes
                    from authbox.config import Config

                    delay_map[k] = Config.parse_time(v)
                except Exception as e:
                    print("Error parsing delay for", k, v, e)
        return delay_map

    def badge_scan(self, badge_id):
        # Malicious badge "numbers" that contain spaces require this extra work.
        command = self._get_command_line("auth", "command", [badge_id])
        # TODO timeout
        # TODO test with missing command
        rc = subprocess.call(command)
        if rc == 0:
            self.buzzer.beep()
            self.authorized = True
            self.badge_id = badge_id
            self.expecting_press_timer.set(30)
            self.on_button.blink()
        else:
            self.off_button.blink(1)
            self.buzzer.beep()
            if self.noise:
                self.noise.kill()
            if self.config.get("sounds", "enable") == "1":
                sound_command = self._get_command_line(
                    "sounds", "command", [self.config.get("sounds", "sad_filename")]
                )
                self.noise = subprocess.Popen(
                    sound_command, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL
                )

    def on_button_down(self, source):
        print("Button down", source)
        if not self.authorized:
            if self.delayed_off_running:
                self.authorized = True
                self.delayed_off_running = False
                self.running_timers_count = 0
                for timer, _ in self.timers.values():
                    timer.cancel()
            else:
                self.off_button.blink(1)
                self.buzzer.beep()
                if self.noise:
                    self.noise.kill()
                if self.config.get("sounds", "enable") == "1":
                    sound_command = self._get_command_line(
                        "sounds", "command", [self.config.get("sounds", "sad_filename")]
                    )
                    self.noise = subprocess.Popen(
                        sound_command, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL
                    )
                return
        self.expecting_press_timer.cancel()
        self.on_button.on()
        self.enable_output.on()
        for timer, _ in self.timers.values():
            timer.cancel()
        self.buzzer.off()
        self.warning_timer.cancel()
        self.expire_timer.cancel()
        # TODO use extend time if we were already enabled, and run its command for
        # logging.
        # N.b. Duration (or extend) includes the warning time.
        self.warning_timer.set(
            self.config.get_int_seconds("auth", "duration", "5m")
            - self.config.get_int_seconds("auth", "warning", "10s")
        )
        self.expire_timer.set(self.config.get_int_seconds("auth", "duration", "5m"))
        if self.noise:
            self.noise.kill()
            self.noise = None

    def abort(self, source):
        print("Abort", source)
        delayed_count = 0
        for obj, delay in self.outputs:
            if delay == 0:
                obj.off()
            else:
                timer, _ = self.timers.get(id(obj), (None, None))
                if timer:
                    timer.cancel()
                    timer.set(delay)
                    delayed_count += 1

        if delayed_count > 0:
            self.delayed_off_running = True
            self.running_timers_count = delayed_count

        if self.authorized:
            command = self._get_command_line("auth", "deauth_command", [self.badge_id])
            subprocess.call(command)
        self.off_button.blink(1)
        self.buzzer.beep()
        self.authorized = False
        self.warning_timer.cancel()
        self.expecting_press_timer.cancel()
        self.expire_timer.cancel()
        self.on_button.off()
        self.buzzer.off()
        if self.noise:
            self.noise.kill()
            self.noise = None

    def delayed_off_generic(self, obj):
        print("Delayed off generic", obj)
        obj.off()
        self.running_timers_count -= 1
        if self.running_timers_count <= 0:
            self.delayed_off_running = False
            self.running_timers_count = 0

    def warning(self, unused_source):
        self.buzzer.beepbeep()
        if self.config.get("sounds", "enable") == "1":
            sound_command = self._get_command_line(
                "sounds", "command", [self.config.get("sounds", "warning_filename")]
            )
            self.noise = subprocess.Popen(
                shlex.split(sound_command),
                stdin=DEVNULL,
                stdout=DEVNULL,
                stderr=DEVNULL,
            )
        self.on_button.blink()


def main(args):
    if not args:
        root = "~"
    else:
        root = args[0]

    config = Config(os.path.join(root, ".authboxrc"))
    Dispatcher(config).run_loop()


if __name__ == "__main__":
    main(sys.argv[1:])
