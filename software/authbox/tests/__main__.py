# flake8: noqa
from unittest import main

from authbox.tests.test_api import (
    ClassRegistryTest,
    DispatcherTest,
    MultiProxyTest,
    SplitEscapedTest,
)
from authbox.tests.test_badgereader_hid_keystroking import BadgereaderTest
from authbox.tests.test_badgereader_wiegand_gpio import BadgereaderWiegandGPIOTest
from authbox.tests.test_config import ConfigTest, RecursiveConfigParamLookupTest
from authbox.tests.test_fake_gpio import FakeGPIOTest
from authbox.tests.test_gpio_button import BlinkTest
from authbox.tests.test_gpio_buzzer import BuzzerTest
from authbox.tests.test_gpio_relay import RelayTest
from authbox.tests.test_timer import TimerTest

main(buffer=True)
