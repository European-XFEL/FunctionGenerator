#############################################################################
# Author: amunnich
# Created on April 04, 2022, 11:06 AM
# Copyright (C) European XFEL GmbH Hamburg. All rights reserved.
#############################################################################

from karabo.middlelayer import Node
from .FunctionGenerator import FunctionGenerator
from .KeysightChannelNode import KeysightChannelNode


class Keysight33512(FunctionGenerator):

    channel_1 = Node(KeysightChannelNode,
                     displayedName='channel 1',
                     alias="1")
    channel_2 = Node(KeysightChannelNode,
                     displayedName='channel 2',
                     alias="2")
