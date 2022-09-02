#############################################################################
# Author: amunnich
# Created on April 04, 2022, 11:06 AM
# Copyright (C) European XFEL GmbH Hamburg. All rights reserved.
#############################################################################
from asyncio import TimeoutError, wait_for

from karabo.middlelayer import (
    AccessMode, Double, Node, State, String, Unit, Slot, background
)

from scpiml import ScpiDevice, ScpiConfigurable

from ._version import version as deviceVersion

CONNECTION_TIMEOUT = 10  # in seconds


class ChannelNode(ScpiConfigurable):

    outputState = String(
        displayedName='Output state',
        alias='OUTPut{channel_no}',
        options={'ON', 'OFF'},
        description={"Enable the AFG output for the specified channel."})
    outputState.readOnConnect = True

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

    functionShape = String(
        displayedName='Function Shape',
        alias='SOURce{channel_no}:FUNCtion:SHAPe',
        options={'SIN', 'SQU', 'PULS', 'RAMP', 'PRN', 'DC', 'SINC', 'GAUS',
                 'LOR', 'ERIS', 'EDEC', 'EMEM'},
        description={"Shape of the output waveform. When the specified user "
                     "memory is deleted, this command causes an error if you "
                     "select the user memory. "
                     "If you select a waveform shape that is not allowed with "
                     "a particular modulation, sweep, or burst, Run mode "
                     "automatically changes to Continuous."},
        defaultValue='PULS')
    functionShape.readOnConnect = True

    def setter(self, value):
        value = str(value)
        try:
            self.functionShape = value
        except ValueError:
            self.status = f"Function shape return value {value} not one " \
                          "of the valid options"

    functionShape.__set__ = setter

    offset = Double(
        displayedName='Offset',
        unitSymbol=Unit.VOLT,
        alias='SOURce{channel_no}:VOLT:OFFS',
        description={"Offset level for the specified channel. "
                     "If your instrument is a dual-channel "
                     "model and the [SOURce[1|2]]:VOLTage:CONCurrent[:STATe] "
                     "command is set to ON, then the offset level of the "
                     "other channel is also the same value."})
    offset.readOnConnect = True
    offset.poll = 10

    amplitude = Double(
        displayedName='Amplitude',
        alias='SOURce{channel_no}:VOLT:AMPL',
        description={"Output amplitude for the specified channel."
                     "Unit is set by amplitude unit value"})
    amplitude.poll = 10
    amplitude.readOnConnect = True

    amplitudeUnit = String(
        displayedName='Amplitude Unit',
        alias='SOURce{channel_no}:VOLT:UNIT',
        options={'VPP', 'VRMS', 'DBM'},
        description={"Units of output amplitude for the specified channel."},
        defaultValue='VPP')
    amplitudeUnit.readOnConnect = True

    pulseWidth = Double(
        displayedName='Pulse width',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:PULS:WIDT',
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
            self.status = f"Invalid value for pulseWidth: {value}." \
                          "Has to be smaller than the " \
                          f"period {self.pulsePeriod}"
        else:
            self.pulseWidth = value

    pulseWidth.__set__ = setter

    pulsePeriod = Double(
        displayedName='Pulse period',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:PULS:PER',
        description={"Period of pulse waveform."})
    pulsePeriod.readOnConnect = True
    pulsePeriod.commandFormat = "{alias} {value} s"

    burstState = String(
        displayedName='Burst State',
        alias='SOURce{channel_no}:BURSt:STAT',
        options={'ON', 'OFF'},
        description={"Enables or disables the burst mode for the "
                     "specified channel."},
        defaultValue='OFF')
    burstState.readOnConnect = True

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

    burstIdle = String(
        displayedName='Burst Idle',
        description='Idle state means the output level between two '
                    'burst output. '
                    'START: The output keep same as the first point of '
                    'burst waveform.'
                    'DC: The output keep the DC.'
                    'END: The output keep same as the end point of burst '
                    'waveform.',
        alias='SOURce{channel_no}:BURSt:IDLE',
        options={'START', 'DC', 'END', 'OFF'},
        defaultValue='OFF')
    burstIdle.readOnConnect = True

    burstMode = String(
        displayedName='Burst Mode',
        alias='SOURce{channel_no}:BURSt:MODE',
        options={'TRIG', 'GAT'},
        description={"TRIG: Means that triggered mode is selected for "
                     "burst mode."
                     "GAT: Means gated mode is selected for burst mode."},
        defaultValue='TRIG')
    burstMode.readOnConnect = True

    burstCycles = String(
        displayedName='Burst Cycles',
        alias='SOURce{channel_no}:BURSt:NCYC',
        description={"Number of cycles (burst count) to be output in burst "
                     "mode for the specified channel. The query command "
                     "returns 9.9E+37 if the burst count is set to INFinity."
                     "Choose a number between 1 and 1,000,000 or "
                     "INF, MIN or MAX"},
        defaultValue='INF')
    burstCycles.readOnConnect = True

    def setter(self, value):
        # convert any answer to string in case of a number
        self.burstCycles = str(value)

    burstCycles.__set__ = setter

    burstDelay = String(
        displayedName='Burst Delay',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:BURS:TDEL',
        description={"Specifies a time delay between the trigger and the "
                     "signal output. This command is available only in the "
                     "Triggered burst mode. "
                     "The setting range is 0.0 ns to 85.000 s with "
                     "resolution of 100 ps or 5 digits."
                     "Choose a number in range or MIN or MAX"},
        defaultValue='MIN')
    burstDelay.readOnConnect = True
    burstDelay.commandFormat = "{alias} {value} s"

    def setter(self, value):
        # convert any answer to string in case of a number
        self.burstDelay = str(value)

    burstDelay.__set__ = setter

    frequency = Double(
        displayedName='Frequency',
        unitSymbol=Unit.HERTZ,
        alias='SOURce{channel_no}:FREQ',
        description={"Frequency of output waveform for the specified channel. "
                     "This command is available when the Run Mode is set to "
                     "other than Sweep. The setting range of output frequency "
                     "depends on the type of output waveform. If you change "
                     "the type of output waveform, it might change the output "
                     "frequency because changing waveform types impacts on "
                     "the setting range of output frequency."})
    frequency.readOnConnect = True
    frequency.commandFormat = "{alias} {value} Hz"

    frequencyStart = Double(
        displayedName='Start Frequency',
        unitSymbol=Unit.HERTZ,
        alias='SOURce{channel_no}:FREQ:STAR',
        description={"Start frequency of sweep for the specified channel. "
                     "This command is always used with the "
                     "[SOURce[1|2]]:FREQuency:STOP command. The setting "
                     "range of start frequency depends on the waveform "
                     "selected for sweep."})
    frequencyStart.readOnConnect = True
    frequencyStart.commandFormat = "{alias} {value} Hz"

    frequencyStop = Double(
        displayedName='Stop Frequency',
        unitSymbol=Unit.HERTZ,
        alias='SOURce{channel_no}:FREQ:STOP',
        description={"Stop frequency of sweep for the specified channel. "
                     "This command is always used with the "
                     "[SOURce[1|2]]:FREQuency:STARt command. The setting "
                     "range of stop frequency depends on the waveform "
                     "selected for sweep."})
    frequencyStop.readOnConnect = True
    frequencyStop.commandFormat = "{alias} {value} Hz"

    sweepTime = Double(
        displayedName='Sweep Time',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:SWE:TIME',
        description={"Sweep time for the sweep for the specified channel. "
                     "The sweep time does not include hold time and return "
                     "time. The setting range is 1 ms to 500 s."})
    sweepTime.readOnConnect = True
    sweepTime.commandFormat = "{alias} {value} s"

    sweepHoldTime = Double(
        displayedName='Sweep Hold Time',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:SWE:HTIM',
        description={"Sweep hold time. Hold time represents the amount of "
                     "time that the frequency must remain stable after "
                     "reaching the stop frequency."})
    sweepHoldTime.readOnConnect = True
    sweepHoldTime.commandFormat = "{alias} {value} s"

    sweepReturnTime = Double(
        displayedName='Sweep Return Time',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:SWE:RTIM',
        description={"Sweep return time. Return time represents the amount "
                     "of time from stop frequency through start frequency. "
                     "Return time does not include hold time."})
    sweepReturnTime.readOnConnect = True
    sweepReturnTime.commandFormat = "{alias} {value} s"

    sweepMode = String(
        displayedName='Sweep Mode',
        alias='SOURce{channel_no}:SWE:MODE',
        options={'AUTO', 'MAN'},
        description={"AUTO: Sets the sweep mode to auto; the instrument "
                     "outputs a continuous sweep at a rate specified by "
                     "Sweep Time, Hold Time, and Return Time."
                     "MAN: Sets the sweep mode to manual; the instrument "
                     "outputs one sweep when a trigger input is received."},
        defaultValue='AUTO')
    sweepMode.readOnConnect = True


class FunctionGenerator(ScpiDevice):
    __version__ = deviceVersion

    # this device does not return anything after commands
    async def readCommandResult(self, descriptor, value):
        return value

    channel_1 = Node(ChannelNode, displayedName='channel 1', alias="1")
    channel_2 = Node(ChannelNode, displayedName='channel 2', alias="2")

    # override methods to create queries and commands for parameters in nodes
    def createChildQuery(self, descr, child):
        if child is None or child is self:
            return self.createQuery(descr)
        else:
            return self.createNodeQuery(descr, child)

    def createNodeQuery(self, descr, child):
        scpi_add = descr.alias.format(channel_no=child.alias)
        return f"{scpi_add}?\n"

    def createChildCommand(self, descr, value, child):
        if child is None or child is self:
            return self.createCommand(descr, value)
        else:
            return self.createNodeCommand(descr, value, child)

    def createNodeCommand(self, descr, value, child):
        scpi_add = descr.alias.format(channel_no=child.alias)
        return (getattr(descr, "commandFormat", self.command_format)
                .format(alias=scpi_add, device=self, value=value.value))

    # CHANNEL independent parameters
    identification = String(
        displayedName='Identification',
        accessMode=AccessMode.READONLY,
        alias='*IDN',
        description={"Identification information on the AFG."})
    identification.readOnConnect = True

    triggerMode = String(
        displayedName='Trigger Mode',
        alias='OUTP:TRIG:MODE',
        options={'TRIG', 'SYNC'},
        description={"The mode (trigger or sync) for Trigger Output signal. "
                     "When the burst count is set to Inf-Cycles in burst mode,"
                     "TRIGger indicates that the infinite number of cycles "
                     "of waveform will be output from the Trigger Output "
                     "connector. When the burst count is set to Inf-Cycles "
                     "in burst mode, SYNC indicates that one pulse waveform "
                     "is output from the Trigger Output connector when the "
                     "Inf-Cycles starts. When Run Mode is specified other "
                     "than Burst Inf-Cycles, TRIGger, and SYNC have the "
                     "same effect."},
        defaultValue='TRIG')
    triggerMode.readOnConnect = True

    triggerSource = String(
        displayedName='Trigger Source',
        alias='TRIG:SOUR',
        options={'TIM', 'EXT'},
        description={"TIM: Specifies an internal clock as the trigger "
                     "source. EXT: use external trigger source"},
        defaultValue='TIM')
    triggerSource.readOnConnect = True

    triggerTime = Double(
        displayedName='Trigger Time',
        alias='TRIG:TIM',
        unitSymbol=Unit.SECOND,
        description={"Period of an internal clock when you select the "
                     "internal clock as the trigger source. "
                     "The setting range is 1 μs to 500.0 s."},
        defaultValue=10)
    triggerTime.readOnConnect = True
    triggerTime.commandFormat = "{alias} {value} s"

    runMode = String(
        displayedName='Run Mode',
        alias='SEQC:RMOD',
        options={'CONT', 'TRIG', 'GAT', 'SEQ'},
        description={"CONT: Sets Run Mode to Continuous."
                     "TRIG: Sets Run Mode to Triggered."
                     "GAT: Sets Run Mode to Gated."
                     "SEQ: Sets Run Mode to Sequence."},
        defaultValue='CONT')
    runMode.readOnConnect = True

    @Slot(
        displayedName="Connect",
        allowedStates=[State.UNKNOWN]
    )
    async def connect(self):
        self.state = State.CHANGING
        self.status = "Connecting..."
        if self.connect_task:
            self.connect_task.cancel()
        self.connect_task = background(self._connect())

    async def _connect(self):
        """Connects to the instrument.

        In case of failures the state is set to UNKNOWN and the device tries
        to reconnect.
        """
        msg = ""
        try:
            await wait_for(super().connect(), timeout=CONNECTION_TIMEOUT)
        except TimeoutError as e:
            if "Timeout while waiting for reply" not in str(e):
                msg = (f"Error: No connection established within "
                       f"timeout ({CONNECTION_TIMEOUT} s). Please, "
                       "fix the network problem and press 'connect'.")
        except ConnectionRefusedError as e:
            msg = ("Error: ConnectionRefused. "
                   f"Exception: {e}. Please, fix the network or hardware "
                   f"problem and press 'connect'.")
        finally:
            # dump a message in case of error and re-try connecting
            if msg:
                if self.status != msg:
                    self.logger.error(msg)
                    self.status = msg
                    self.state = State.UNKNOWN
                self.connect_task = background(self._connect())
                return False

        self.status = "Connected"

        return True

    async def onInitialization(self):
        self.initialized = True
        self.connect_task = None
        self.connect_task = await self.connect()

    async def onDestruction(self):
        """Actions to take when the device is shutdown."""
        if self.connect_task:  # connecting
            self.connect_task.cancel()
        if self.state != State.UNKNOWN:
            await self.close_connection()
        await super().onDestruction()
