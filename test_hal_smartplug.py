# encoding: utf-8
"""
High level test for hal_smartplug component

Copyright Alexander Rössler <mail AT roessler DOT systems>
"""

from nose import with_setup
from machinekit.nosetests.realtime import setup_module ,teardown_module
from machinekit.nosetests.support import fnear
from unittest import TestCase
import time

from machinekit import hal
from machinekit import rtapi


ADDRESS = "10.0.0.8"


class TestHalSmartplug(TestCase):
    def setUp(self):
        pass
        #rt = rtapi.RTAPIcommand()
    #    rt.newthread("servo-thread", 1000000, fp=True)
    #    hal.start_threads()

    def test_smartplug(self):
        # create system under test (sut)
        sut = hal.loadusr('./hal_smartplug.py -n sut -e -a %s' % ADDRESS, wait_name='sut')
        time.sleep(1.0)  # wait for system to connect

        pin = sut.pin('enable')
        self.assertTrue(pin.type == hal.HAL_BIT, "type mismatch")
        self.assertTrue(pin.dir == hal.HAL_IO, "dir mismatch")
        pin = sut.pin('error')
        self.assertTrue(pin.type == hal.HAL_BIT, "type mismatch")
        self.assertTrue(pin.dir == hal.HAL_OUT, "dir mismatch")
        pin = sut.pin('current')
        self.assertTrue(pin.type == hal.HAL_FLOAT, "type mismatch")
        self.assertTrue(pin.dir == hal.HAL_OUT, "dir mismatch")
        pin = sut.pin('voltage')
        self.assertTrue(pin.type == hal.HAL_FLOAT, "type mismatch")
        self.assertTrue(pin.dir == hal.HAL_OUT, "dir mismatch")
        pin = sut.pin('power')
        self.assertTrue(pin.type == hal.HAL_FLOAT, "type mismatch")
        self.assertTrue(pin.dir == hal.HAL_OUT, "dir mismatch")
        pin = sut.pin('energy')
        self.assertTrue(pin.type == hal.HAL_FLOAT, "type mismatch")
        self.assertTrue(pin.dir == hal.HAL_OUT, "dir mismatch")

        error = sut.pin('error')
        self.assertTrue(error.get() == 0, "Smartplug not online")

        enable = sut.pin('enable')
        enable.set(False)
        time.sleep(1.1)
        self.assertFalse(error.get())
        enable.set(True)
        time.sleep(1.1)
        self.assertFalse(error.get())
        enable.set(False)
        time.sleep(1.1)
        self.assertFalse(error.get())
        enable.set(True)
        time.sleep(1.1)
        self.assertFalse(error.get())
        enable.set(False)
        time.sleep(1.1)
        self.assertFalse(error.get())

    def test_smartplug_without_emeter(self):
        sut = hal.loadusr('./hal_smartplug.py -n sut2 -a %s' % ADDRESS, wait_name='sut2')
        time.sleep(1.0)  # wait for system to connect

        pin = sut.pin('enable')
        self.assertTrue(pin.type == hal.HAL_BIT, "type mismatch")
        self.assertTrue(pin.dir == hal.HAL_IO, "dir mismatch")
        pin = sut.pin('error')
        self.assertTrue(pin.type == hal.HAL_BIT, "type mismatch")
        self.assertTrue(pin.dir == hal.HAL_OUT, "dir mismatch")
        found = False
        try:
            sut.pin('current')
            found = True
        except RuntimeError:
            pass
        self.assertFalse(found, "Pin current should not exist")

        error = sut.pin('error')
        self.assertTrue(error.get() == 0, "Smartplug not online")

        enable = sut.pin('enable')
        enable.set(False)
        time.sleep(1.1)
        self.assertFalse(error.get())
        enable.set(True)
        time.sleep(1.1)
        self.assertFalse(error.get())
        enable.set(False)
        time.sleep(1.1)
        self.assertFalse(error.get())
        enable.set(True)
        time.sleep(1.1)
        self.assertFalse(error.get())
        enable.set(False)
        time.sleep(1.1)
        self.assertFalse(error.get())
