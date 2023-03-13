#############################################################################
# Author: amunnich
# Created on April 04, 2022, 11:06 AM
# Copyright (C) European XFEL GmbH Hamburg. All rights reserved.
#############################################################################

from karabo.middlelayer import (
    AccessMode, Assignment, Double, KaraboValue, Overwrite, State,
    String, Unit, Slot
)

from scpiml import ScpiAutoDevice, ScpiConfigurable

from ._version import version as deviceVersion


class ChannelNodeBase(ScpiConfigurable):

    # also needed as global value in the node as it will be the 'self' when
    # scpiML uses the following attributes
    commandReadBack = True
    readOnConnect = True

    def on_off_setter(self, value, key):
        if value not in ('ON', 'OFF'):
            try:
                value = int(value)
                if value == 0:
                    value = 'OFF'
                elif value == 1:
                    value = 'ON'
            except ValueError:
                pass

        try:
            setattr(self, key, value)
        except ValueError as e:
            msg = f"{key} return value {value} is not one " \
                  "of the valid options"
            self.status = msg
            raise e

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
        description="Enable the output for the channel.",
        assignment=Assignment.INTERNAL)

    def output_state_setter(self, value):
        self.on_off_setter(value, "outputState")

    outputState.__set__ = output_state_setter

    outputPol = String(
        displayedName='Output Polarity',
        alias='OUTPut{channel_no}:POL',
        options={'NORM', 'INV'},
        description="Inverts waveform relative to offset voltage.",
        assignment=Assignment.INTERNAL)

    offset = Double(
        displayedName='Offset',
        unitSymbol=Unit.VOLT,
        alias='SOURce{channel_no}:VOLT:OFFS',
        description="Offset level for the specified channel.",
        assignment=Assignment.INTERNAL)
    offset.poll = True

    amplitude = Double(
        displayedName='Amplitude',
        alias='SOURce{channel_no}:VOLT',
        description="Output amplitude for the specified channel. "
                    "Unit is set by amplitude unit value.",
        assignment=Assignment.INTERNAL)
    amplitude.poll = True

    amplitudeUnit = String(
        displayedName='Amplitude Unit',
        alias='SOURce{channel_no}:VOLT:UNIT',
        options={'VPP', 'VRMS', 'DBM'},
        description="Units of output amplitude for the specified channel.",
        defaultValue='VPP',
        assignment=Assignment.INTERNAL)

    voltageLow = Double(
        displayedName='Voltage Low',
        unitSymbol=Unit.VOLT,
        alias='SOURce{channel_no}:VOLT:LOW',
        description={"Waveform low voltage"},
        assignment=Assignment.INTERNAL)
    voltageLow.poll = True

    voltageHigh = Double(
        displayedName='Voltage High',
        unitSymbol=Unit.VOLT,
        alias='SOURce{channel_no}:VOLT:HIGH',
        description="Waveform high voltage.",
        assignment=Assignment.INTERNAL)
    voltageHigh.poll = True

    frequency = Double(
        displayedName='Frequency',
        unitSymbol=Unit.HERTZ,
        alias='SOURce{channel_no}:FREQ',
        description="Frequency of arbitrary waveform for the channel.",
        assignment=Assignment.INTERNAL)
    frequency.poll = True

    phase = Double(
        displayedName='Phase',
        alias='SOURce{channel_no}:PHASe',
        description="Phase offset angle of waveform for the channel.",
        assignment=Assignment.INTERNAL)
    phase.poll = True

    burstState = String(
        displayedName='Burst State',
        alias='SOURce{channel_no}:BURSt:STAT',
        options={'ON', 'OFF'},
        description="Enables or disables the burst mode for the "
                    "specified channel.",
        defaultValue='OFF',
        assignment=Assignment.INTERNAL)
    burstState.poll = True

    def burst_state_setter(self, value):
        self.on_off_setter(value, "burstState")

    burstState.__set__ = burst_state_setter

    burstMode = String(
        displayedName='Burst Mode',
        alias='SOURce{channel_no}:BURSt:MODE',
        options={'TRIG', 'GAT'},
        description="TRIG: Means that triggered mode is selected for "
                    "burst mode. "
                    "GAT: Means gated mode is selected for burst mode.",
        defaultValue='TRIG',
        assignment=Assignment.INTERNAL)

    burstCycles = String(
        displayedName='Burst Cycles',
        alias='SOURce{channel_no}:BURSt:NCYC',
        description="Number of cycles (burst count) to be output in burst "
                    "mode for the specified channel.",
        defaultValue='INF',
        assignment=Assignment.INTERNAL)

    def burst_cycles_setter(self, value):
        # convert any answer to string in case of a number
        self.burstCycles = str(value)

    burstCycles.__set__ = burst_cycles_setter

    frequencyStart = Double(
        displayedName='Start Frequency',
        unitSymbol=Unit.HERTZ,
        alias='SOURce{channel_no}:FREQ:STAR',
        description="Start frequency of sweep for the specified channel.",
        assignment=Assignment.INTERNAL)

    frequencyStop = Double(
        displayedName='Stop Frequency',
        unitSymbol=Unit.HERTZ,
        alias='SOURce{channel_no}:FREQ:STOP',
        description="Stop frequency of sweep for the specified channel.",
        assignment=Assignment.INTERNAL)

    sweepTime = Double(
        displayedName='Sweep Time',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:SWE:TIME',
        description="Sweep time for the sweep for the specified channel.",
        assignment=Assignment.INTERNAL)

    sweepHoldTime = Double(
        displayedName='Sweep Hold Time',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:SWE:HTIM',
        description="Sweep hold time.",
        assignment=Assignment.INTERNAL)

    sweepReturnTime = Double(
        displayedName='Sweep Return Time',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:SWE:RTIM',
        description="Sweep return time. Return time represents the amount "
                    "of time from stop frequency through start frequency.",
        assignment=Assignment.INTERNAL)


class FunctionGenerator(ScpiAutoDevice):
    __version__ = deviceVersion

    # no reply on commands, so we query on all attributes after set
    commandReadBack = True
    readOnConnect = True

    # CHANNEL independent parameters
    identification = String(
        displayedName='Identification',
        accessMode=AccessMode.READONLY,
        alias='*IDN',
        description="Identification information.")

    systemError = String(
        displayedName='System error',
        accessMode=AccessMode.READONLY,
        alias='SYSTem:ERRor',
        description="System Error raised on hardware.")
    systemError.poll = True

    def system_error_setter(self, value):
        if "No error" in value:
            pass
        else:
            self.systemError = value

    systemError.__set__ = system_error_setter

    # set a larger value to allow manual interaction with hardware while
    # karabo device is connected
    pollingInterval = Overwrite(defaultValue=5, maxInc=600)

    @Slot(
        displayedName="Reset",
        allowedStates=[State.ERROR]
    )
    async def reset(self):
        if self.connected:
            self.state = State.NORMAL
        else:
            self.state = State.UNKNOWN

    # create the nodes in the specific implementation inheriting from
    # ChannelNodeBase
    # channel_1 = Node(ChannelNodeBase, displayedName='channel 1', alias="1")
    # channel_2 = Node(ChannelNodeBase, displayedName='channel 2', alias="2")

    # this device does not return anything after commands
    async def readCommandResult(self, descriptor, value):
        # exception for query commands that do return a response
        if descriptor.key in ["arbs", "catalog", "currentArbForm"]:
            return await self.get_root().readQueryResult(descriptor)
        else:
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
        value = self.func_shape_decode.get(value, value)
        return (getattr(descr, "commandFormat", self.command_format)
                .format(alias=scpi_add, device=self, value=value))

    func_shape_decode = {'Sine': 'SIN',
                         'Square': 'SQU',
                         'Ramp': 'RAMP',
                         'Triangle': 'TRI',
                         'Pulse': 'PULS',
                         'Noise': 'NOIS',
                         'PRBS': 'PRBS',
                         'Arbitrary': 'ARB',
                         'DC': 'DC',
                         'PR Noise': 'PRN',
                         'Sin(x)/x': 'SINC',
                         'Lorentz': 'LOR',
                         'Exponential Rise': 'ERSI',
                         'Exponential Decay': 'EDEC',
                         'Harvesine': 'HAV'}
