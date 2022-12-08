#############################################################################
# Author: amunnich
# Created on April 04, 2022, 11:06 AM
# Copyright (C) European XFEL GmbH Hamburg. All rights reserved.
#############################################################################

from karabo.middlelayer import (
    AccessMode, Double, Node, State, String, Unit, Slot, background
)

from scpiml import ScpiConfigurable

from ._version import version as deviceVersion
from .FunctionGenerator import FunctionGenerator


class KeysightChannelNode(ScpiConfigurable):

    pulseWidth = Double(
        displayedName='Pulse width',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:FUNC:PULS:WIDT',
        description={"Pulse Width = Period * Duty Cycle / 100"
                     "The pulse width must be less than the period. "
                     "The setting range is 0.001% to 99.999% in terms of "
                     "duty cycle."})
    pulseWidth.readOnConnect = True
    pulseWidth.commandFormat = "{alias} {value} s"

    def setter(self, value):
        #  check if value in allowed range for period set
        if not self.pulsePeriod:
            self.pulseWidth = value
            return
        if value > self.pulsePeriod:
            # TODO: code gets here but status is not shown in GUI
            self.status = f"Invalid value for pulseWidth: {value}." \
                          "Has to be smaller than the " \
                          f"period {self.pulsePeriod}"
        else:
            self.pulseWidth = value

    pulseWidth.__set__ = setter

    pulsePeriod = Double(
        displayedName='Pulse period',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:FUNC:PULS:PER',
        description={"Period of pulse waveform."})
    pulsePeriod.readOnConnect = True
    pulsePeriod.commandFormat = "{alias} {value} s"

    frequency = Double(
        displayedName='Frequency',
        unitSymbol=Unit.HERTZ,
        alias='SOURce{channel_no}:FUNCtion:ARBitrary:FREQ',
        description={"Frequency of output waveform for the specified channel. "
                     "This command is available when the Run Mode is set to "
                     "other than Sweep. The setting range of output frequency "
                     "depends on the type of output waveform. If you change "
                     "the type of output waveform, it might change the output "
                     "frequency because changing waveform types impacts on "
                     "the setting range of output frequency."})
    frequency.readOnConnect = True
    frequency.commandFormat = "{alias} {value} Hz"

    triggerSource = String(
        displayedName='Trigger Source',
        alias='TRIG{channel_no}:SOUR',
        options={'TIM', 'EXT'},
        description={"TIM: Specifies an internal clock as the trigger "
                     "source. EXT: use external trigger source"},
        defaultValue='TIM')
    triggerSource.readOnConnect = True

    triggerTime = Double(
        displayedName='Trigger Time',
        alias='TRIG{channel_no}:TIM',
        unitSymbol=Unit.SECOND,
        description={"Period of an internal clock when you select the "
                     "internal clock as the trigger source. "
                     "The setting range is 1 μs to 500.0 s."},
        defaultValue=10)
    triggerTime.readOnConnect = True
    triggerTime.commandFormat = "{alias} {value} s"


class Keysight3500(FunctionGenerator):
    __version__ = deviceVersion

    async def onInitialization(self):
        # inject keysight specific parameters
        self.__class__.keysight_ch_1 = Node(KeysightChannelNode,
                             displayedName='keysight ch 1', alias="1")
        self.__class__.keysight_ch_2 = Node(KeysightChannelNode,
                             displayedName='keysight ch 2', alias="2")
        await self.publishInjectedParameters()
        await super.onInitialization()