#############################################################################
# Author: amunnich
# Created on April 04, 2022, 11:06 AM
# Copyright (C) European XFEL GmbH Hamburg. All rights reserved.
#############################################################################

from karabo.middlelayer import (
    AccessMode, Double, KaraboValue, State, String, Unit, Slot
)

from scpiml import ScpiAutoDevice, ScpiConfigurable

from ._version import version as deviceVersion


class ChannelNodeBase(ScpiConfigurable):

    @Slot(displayedName="On", allowedStates=[State.NORMAL])
    async def channelOn(self):
        descr = getattr(self.__class__, "outputState")
        await descr.setter(self, "ON")

    @Slot(displayedName="Off", allowedStates=[State.NORMAL])
    async def channelOff(self):
        descr = getattr(self.__class__, "outputState")
        await descr.setter(self, "OFF")

    outputState = String(
        displayedName='Output State',
        alias='OUTPut{channel_no}',
        options={'ON', 'OFF'},
        description="Enable the output for the channel.")
    outputState.readOnConnect = True
    outputState.commandReadBack = True

    def setter(self, value):
        # convert any answer to string in case of a number
        try:
            if value == 0 or value == '0' or value == "OFF":
                self.outputState = 'OFF'
            elif value != 0 or value == '1' or value == "ON":
                self.outputState = 'ON'
            else:
                self.status = f"Unknown value received for Output " \
                              f"State: {value}"

        except ValueError:
            self.status = f"Output return value {value} not one " \
                          "of the valid options"

    outputState.__set__ = setter

    outputPol = String(
        displayedName='Output Polarity',
        alias='OUTPut{channel_no}:POL',
        options={'NORM', 'INV'},
        description="Inverts waveform relative to offset voltage.")
    outputPol.readOnConnect = True
    outputPol.commandReadBack = True

    offset = Double(
        displayedName='Offset',
        unitSymbol=Unit.VOLT,
        alias='SOURce{channel_no}:VOLT:OFFS',
        description="Offset level for the specified channel.")
    offset.readOnConnect = True
    offset.commandReadBack = True
    offset.poll = 10

    amplitude = Double(
        displayedName='Amplitude',
        alias='SOURce{channel_no}:VOLT',
        description="Output amplitude for the specified channel. "
                    "Unit is set by amplitude unit value.")
    amplitude.readOnConnect = True
    amplitude.commandReadBack = True
    amplitude.poll = 10

    amplitudeUnit = String(
        displayedName='Amplitude Unit',
        alias='SOURce{channel_no}:VOLT:UNIT',
        options={'VPP', 'VRMS', 'DBM'},
        description="Units of output amplitude for the specified channel.",
        defaultValue='VPP')
    amplitudeUnit.readOnConnect = True
    amplitudeUnit.commandReadBack = True

    voltageLow = Double(
        displayedName='Voltage Low',
        unitSymbol=Unit.VOLT,
        alias='SOURce{channel_no}:VOLT:LOW',
        description={"Waveform low voltage"})
    voltageLow.readOnConnect = True
    voltageLow.commandReadBack = True

    voltageHigh = Double(
        displayedName='Voltage High',
        unitSymbol=Unit.VOLT,
        alias='SOURce{channel_no}:VOLT:HIGH',
        description="Waveform high voltage.")
    voltageHigh.readOnConnect = True
    voltageHigh.commandReadBack = True

    frequency = Double(
        displayedName='Frequency',
        unitSymbol=Unit.HERTZ,
        alias='SOURce{channel_no}:FUNCtion:ARBitrary:FREQ',
        description="Frequency of arbitrary waveform for the channel.")
    frequency.readOnConnect = True
    frequency.commandReadBack = True

    burstState = String(
        displayedName='Burst State',
        alias='SOURce{channel_no}:BURSt:STAT',
        options={'ON', 'OFF'},
        description="Enables or disables the burst mode for the "
                    "specified channel.",
        defaultValue='OFF')
    burstState.readOnConnect = True
    burstState.commandReadBack = True

    def setter(self, value):
        # convert any answer to string in case of a number
        try:
            if value == 0 or value == '0' or value == "OFF":
                self.burstState = 'OFF'
            elif value != 0 or value == '1' or value == "ON":
                self.burstState = 'ON'
            else:
                self.burstState = str(value)

        except ValueError:
            self.status = f"Burst state return value {value} not one " \
                          "of the valid options"

    burstState.__set__ = setter

    burstMode = String(
        displayedName='Burst Mode',
        alias='SOURce{channel_no}:BURSt:MODE',
        options={'TRIG', 'GAT'},
        description="TRIG: Means that triggered mode is selected for "
                    "burst mode. "
                    "GAT: Means gated mode is selected for burst mode.",
        defaultValue='TRIG')
    burstMode.readOnConnect = True
    burstMode.commandReadBack = True

    burstCycles = String(
        displayedName='Burst Cycles',
        alias='SOURce{channel_no}:BURSt:NCYC',
        description="Number of cycles (burst count) to be output in burst "
                    "mode for the specified channel.",
        defaultValue='INF')
    burstCycles.readOnConnect = True
    burstCycles.commandReadBack = True

    def setter(self, value):
        # convert any answer to string in case of a number
        self.burstCycles = str(value)

    burstCycles.__set__ = setter

    frequencyStart = Double(
        displayedName='Start Frequency',
        unitSymbol=Unit.HERTZ,
        alias='SOURce{channel_no}:FREQ:STAR',
        description="Start frequency of sweep for the specified channel.")
    frequencyStart.readOnConnect = True
    frequencyStart.commandReadBack = True

    frequencyStop = Double(
        displayedName='Stop Frequency',
        unitSymbol=Unit.HERTZ,
        alias='SOURce{channel_no}:FREQ:STOP',
        description="Stop frequency of sweep for the specified channel.")
    frequencyStop.readOnConnect = True
    frequencyStop.commandReadBack = True

    sweepTime = Double(
        displayedName='Sweep Time',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:SWE:TIME',
        description="Sweep time for the sweep for the specified channel.")
    sweepTime.readOnConnect = True
    sweepTime.commandReadBack = True

    sweepHoldTime = Double(
        displayedName='Sweep Hold Time',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:SWE:HTIM',
        description="Sweep hold time.")
    sweepHoldTime.readOnConnect = True
    sweepHoldTime.commandReadBack = True

    sweepReturnTime = Double(
        displayedName='Sweep Return Time',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:SWE:RTIM',
        description="Sweep return time. Return time represents the amount "
                    "of time from stop frequency through start frequency.")
    sweepReturnTime.readOnConnect = True
    sweepReturnTime.commandReadBack = True


class FunctionGenerator(ScpiAutoDevice):
    __version__ = deviceVersion

    # CHANNEL independent parameters
    identification = String(
        displayedName='Identification',
        accessMode=AccessMode.READONLY,
        alias='*IDN',
        description="Identification information on the AFG.")
    identification.readOnConnect = True

    @Slot(
        displayedName="Reset",
        allowedStates=[State.ERROR]
    )
    async def reset(self):
        self.state = State.NORMAL

    # create the nodes in the specific implementation inheriting from
    # ChannelNodeBase
    # channel_1 = Node(ChannelNodeBase, displayedName='channel 1', alias="1")
    # channel_2 = Node(ChannelNodeBase, displayedName='channel 2', alias="2")

    # this device does not return anything after commands
    async def readCommandResult(self, descriptor, value, child):
        if value:
            child = self if child is None else child
            descriptor.__set__(child, value)
        return None

    # override methods to create queries and commands for parameters in nodes
    def createNodeQuery(self, descr, child):
        scpi_add = descr.alias.format(channel_no=child.alias)
        return f"{scpi_add}?\n"

    def createNodeCommand(self, descr, value, child):
        scpi_add = descr.alias.format(channel_no=child.alias)
        value = value.value if isinstance(value, KaraboValue) else value
        # special treatment for functionShape to map human readable options
        # to scpi command/returns
        func_shape_dict = {'Sine': 'SIN',
                           'Square': 'SQU',
                           'Ramp': 'RAMP',
                           'Triangle': 'TRI',
                           'Pulse': 'PULS',
                           'Noise': 'NOIS',
                           'PRBS': 'PRBS',
                           'Arbitrary': 'ARB',
                           'DC': 'DC'}
        if value in func_shape_dict.keys():
            value = func_shape_dict[value]
        return (getattr(descr, "commandFormat", self.command_format)
                .format(alias=scpi_add, device=self, value=value))
