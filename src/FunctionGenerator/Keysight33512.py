#############################################################################
# Author: amunnich
# Created on April 04, 2022, 11:06 AM
# Copyright (C) European XFEL GmbH Hamburg. All rights reserved.
#############################################################################
from asyncio import sleep
from karabo.middlelayer import (
    AccessMode, Int32, Node, Slot, State, String, get_property, set_property
)
from .FunctionGenerator import FunctionGenerator
from .KeysightChannelNode import KeysightChannelNode


class Keysight33512(FunctionGenerator):

    channel_1 = Node(KeysightChannelNode,
                     displayedName='channel 1',
                     alias="1")
    channel_2 = Node(KeysightChannelNode,
                     displayedName='channel 2',
                     alias="2")

    lockOwner = String(
        displayedName='Lock Owner',
        accessMode=AccessMode.READONLY,
        alias='SYST:LOCK:OWN',
        description="Interface holding the lock.")
    lockOwner.readOnConnect = True
    lockOwner.commandReadBack = True
    lockOwner.poll = 10

    lockRequest = Int32(
        displayedName='Lock Request Count',
        accessMode=AccessMode.READONLY,
        alias='SYST:LOCK:REQ',
        description="Counts locks requested.")
    lockRequest.readOnConnect = True
    lockRequest.commandReadBack = True

    lockRelease = Int32(
        displayedName='Lock Release Count',
        accessMode=AccessMode.READONLY,
        alias='SYST:LOCK:REL',
        description="Counts active locks.")
    lockRelease.commandReadBack = True

    @Slot(displayedName="Get Lock", allowedStates=[State.NORMAL])
    async def getLock(self):
        await self.sendCommand(getattr(self.__class__, "lockRequest"))
        await self.sendQuery(getattr(self.__class__, "lockOwner"))

    @Slot(displayedName="Release Lock", allowedStates=[State.NORMAL])
    async def releaseLock(self):
        await self.sendCommand(getattr(self.__class__, "lockRelease"))
        await self.sendQuery(getattr(self.__class__, "lockOwner"))

    @Slot(displayedName="Channel 1 On", allowedStates=[State.NORMAL])
    async def channel1On(self):
        #AttributeError: 'Node' object has no attribute 'outputState'
        # descr = get_property(self.__class__, "channel_1.outputState")
        chan_node = getattr(self, "channel_1")
        descr = getattr(chan_node.__class__, "outputState")
        # nothing happens
        await self.sendCommand(descr, "ON")

