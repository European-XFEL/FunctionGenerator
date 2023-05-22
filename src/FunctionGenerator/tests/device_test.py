#############################################################################
# Author: amunnich
# Created on April 04, 2022, 11:06 AM
# Copyright (C) European XFEL GmbH Schenefeld. All rights reserved.
#############################################################################
from contextlib import contextmanager

from karabo.middlelayer_api.tests.eventloop import DeviceTest, async_tst

from ..FunctionGenerator import FunctionGenerator

conf = {
    "classId": "FunctionGenerator",
    "_deviceId_": "TestFunctionGenerator",
    "url": ""
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
        pass
