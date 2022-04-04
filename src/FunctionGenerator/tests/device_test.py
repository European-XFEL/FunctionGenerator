#############################################################################
# Author: amunnich
# Created on April 04, 2022, 11:06 AM
# Copyright (C) European XFEL GmbH Hamburg. All rights reserved.
#############################################################################
from contextlib import contextmanager

from karabo.middlelayer_api.tests.eventloop import async_tst, DeviceTest

from ..FunctionGenerator import FunctionGenerator


conf = {
    "classId": "FunctionGenerator",
    "_deviceId_": "TestFunctionGenerator",
    "greeting": "buongiorno"
}


class TestFunctionGenerator(DeviceTest):
    @classmethod
    @contextmanager
    def lifetimeManager(cls):
        cls.dev = FunctionGenerator(conf)
        with cls.deviceManager(lead=cls.dev):
            yield

    @async_tst
    async def test_greet(self):
        for greet in ("Buongiorno", "Guten Tag", "Moin Moin"):
            self.dev.greeting = greet
            self.assertEqual(self.dev.greeting.value, greet)
            await self.dev.hello()
            self.assertEqual(self.dev.greeting.value, "Hello world!")
