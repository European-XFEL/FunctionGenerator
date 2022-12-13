#############################################################################
# Author: amunnich
# Created on April 04, 2022, 11:06 AM
# Copyright (C) European XFEL GmbH Hamburg. All rights reserved.
#############################################################################

from karabo.middlelayer import (
    Double, Node, String, Unit
)

from ._version import version as deviceVersion
from .FunctionGenerator import FunctionGenerator, ChannelNodeBase


class KeysightChannelNode(ChannelNodeBase):

    outputPol = String(
        displayedName='Output polarity',
        alias='OUTPut{channel_no}:POL',
        options={'NORM', 'INV'},
        description={"Inverts waveform relative to offset voltage."})
    outputPol.readOnConnect = True

    outputLoad = Double(
        displayedName='Output load',
        alias='OUTPut{channel_no}:LOAD',
        description={"Sets expected output termination.."})
    outputLoad.readOnConnect = True

    voltageLow = Double(
        displayedName='Voltage Low',
        unitSymbol=Unit.VOLT,
        alias='SOURce{channel_no}:VOLT:LOW',
        description={"Waveform low voltage"})
    voltageLow.readOnConnect = True
    voltageLow.poll = 10

    voltageHigh = Double(
        displayedName='Voltage High',
        unitSymbol=Unit.VOLT,
        alias='SOURce{channel_no}:VOLT:HIGH',
        description={"Waveform high voltage"})
    voltageHigh.readOnConnect = True
    voltageHigh.poll = 10

    functionShape = String(
        displayedName='Function Shape',
        alias='SOURce{channel_no}:FUNCtion',
        options={'SIN', 'SQU', 'RAMP', 'NRAM', 'TRI', 'PULS', 'NOIS',
                 'PRBS', 'ARB', 'DC'},
        description={"Selects the output function"},
        defaultValue='SIN')
    functionShape.readOnConnect = True

    def setter(self, value):
        value = str(value)
        try:
            self.functionShape = value
        except ValueError:
            self.status = f"Function shape return value {value} not one " \
                          "of the valid options"

    functionShape.__set__ = setter

    pulseWidth = Double(
        displayedName='Pulse width',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:FUNC:PULS:WIDT',
        description={"Pulse width is the time from the 50% threshold of a "
                     "pulse's rising edge to the 50% threshold of the next "
                     "falling edge."})
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

    arbitraryForm = String(
        displayedName='Arbitrary Form',
        alias='SOURce{channel_no}:FUNC:ARB',
        description={"File with arbitrary waveform."})
    arbitraryForm.readOnConnect = True
    arbitraryForm.commandFormat = "{alias} {value} s"

    arbitraryPeriod = Double(
        displayedName='Arbitrary period',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:FUNC:ARB:PER',
        description={"Period of arbitrary waveform."})
    arbitraryPeriod.readOnConnect = True
    arbitraryPeriod.commandFormat = "{alias} {value} s"

    rampSymmetry = Double(
        displayedName='Ramp Symmetry',
        alias='SOURce{channel_no}:FUNC:RAMP:SYMM',
        description={"Symmetry of ramp waveform in percent."})
    rampSymmetry.readOnConnect = True
    rampSymmetry.commandFormat = "{alias} {value} s"

    triggerSource = String(
        displayedName='Trigger Source',
        alias='TRIG{channel_no}:SOUR',
        options={'TIM', 'EXT', "BUS", "IMM"},
        description={"Selects the trigger source. Immediate or timed internal "
                     "trigger, external or software (BUS) trigger."},
        defaultValue='TIM')
    triggerSource.readOnConnect = True

    triggerTime = Double(
        displayedName='Trigger Time',
        alias='TRIG{channel_no}:TIM',
        unitSymbol=Unit.SECOND,
        description={"Period of an internal clock when you select the "
                     "internal clock as the trigger source."},
        defaultValue=10)
    triggerTime.readOnConnect = True
    triggerTime.commandFormat = "{alias} {value} s"


class Keysight3500(FunctionGenerator):
    __version__ = deviceVersion

    async def onInitialization(self):
        # inject keysight specific parameters
        self.__class__.ch_1 = Node(KeysightChannelNode,
                                   displayedName='channel 1',
                                   alias="1")
        self.__class__.ch_2 = Node(KeysightChannelNode,
                                   displayedName='channel 2',
                                   alias="2")
        await self.publishInjectedParameters()
        await super().onInitialization()
