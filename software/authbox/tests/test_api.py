# Copyright 2018 Google Inc. All Rights Reserved.
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

"""Tests for authbox.api"""

import tempfile
import unittest

import authbox.api
import authbox.config
import authbox.gpio_button

SAMPLE_CONFIG = b"""
[pins]
button_a = Button:1:2
button_b = Button
button_c = Button:1:2:3:4:5
button_multi = Button:1:2, Button:3:4
bad = MissingClass:1:2
"""


class ClassRegistryTest(unittest.TestCase):
    def test_no_duplicate_names(self):
        short_names = {name.split(".")[-1] for name in authbox.api.CLASS_REGISTRY}
        self.assertEqual(len(short_names), len(authbox.api.CLASS_REGISTRY))

    def test_all_names_importable(self):
        for c in authbox.api.CLASS_REGISTRY:
            cls = authbox.api._import(c)
            assert issubclass(
                cls, (authbox.api.BasePinThread, authbox.api.BaseDerivedThread)
            ), (c, cls, cls.__bases__)


class DispatcherTest(unittest.TestCase):
    def setUp(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(SAMPLE_CONFIG)
            f.flush()
            config = authbox.config.Config(f.name)
        self.dispatcher = authbox.api.BaseDispatcher(config)

    def test_load_config_object(self):
        self.dispatcher.load_config_object("button_a")
        self.assertIsInstance(self.dispatcher.button_a, authbox.gpio_button.Button)
        self.assertEqual(self.dispatcher.button_a.input_pin, 1)
        self.assertEqual(self.dispatcher.button_a.output_pin, 2)

    def test_load_config_object_multiproxy(self):
        self.dispatcher.load_config_object("button_multi")
        self.assertIsInstance(self.dispatcher.button_multi, authbox.api.MultiProxy)

    def test_load_config_object_raises(self):
        # TODO: Needs a better exception
        self.assertRaises(Exception, lambda: self.dispatcher.load_config_object("bad"))


class T(object):
    def __init__(self):
        self.called = 0
        self.args = None
        self.kwargs = None

    def meth(self, *args, **kwargs):
        self.called += 1
        self.args = args
        self.kwargs = kwargs


class MultiProxyTest(unittest.TestCase):
    def setUp(self):
        self.a = T()
        self.b = T()
        self.c = T()

        self.mp = authbox.api.MultiProxy([self.a, self.b, self.c])

    def test_missing_method_behavior(self):
        self.mp.meth
        self.assertRaises(AttributeError, lambda: self.mp.foo)

    def test_all_are_called(self):
        self.mp.meth("a", key="val")
        self.assertEqual(self.a.args, ("a",))
        self.assertEqual(self.b.args, ("a",))
        self.assertEqual(self.c.args, ("a",))


class SplitEscapedTest(unittest.TestCase):
    def test_normal(self):
        result = list(authbox.api.split_escaped("a,b,c"))
        self.assertEqual(result, ["a", "b", "c"])

    def test_preserves_whitespace(self):
        result = list(authbox.api.split_escaped(" a, b "))
        self.assertEqual(result, [" a", " b "])

    def test_alternate_glue(self):
        result = list(authbox.api.split_escaped("a|b", glue="|"))
        self.assertEqual(result, ["a", "b"])

    def test_escapes(self):
        result = list(authbox.api.split_escaped(r"a\\,\,b"))
        self.assertEqual(result, ["a\\", ",b"])

    def test_preserve(self):
        result = list(authbox.api.split_escaped(r"a\\,\,b", preserve=True))
        self.assertEqual(result, ["a\\\\", "\\,b"])
