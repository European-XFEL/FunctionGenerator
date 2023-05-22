#############################################################################
# Author: amunnich
# Created on April 04, 2022, 11:06 AM
# Copyright (C) European XFEL GmbH Schenefeld. All rights reserved.
#############################################################################

from karabo.middlelayer import Node

from .KeysightBase import KeysightBase
from .KeysightChannelNode import KeysightChannelNode


class Keysight33511(KeysightBase):

    channel_1 = Node(KeysightChannelNode,
                     displayedName='channel 1',
                     alias="1")

    async def onInitialization(self):
        # get the parent base class into the channel node
        self.channel_1.setup(self.parent)
