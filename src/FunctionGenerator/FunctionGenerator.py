#############################################################################
# Author: amunnich
# Created on April 04, 2022, 11:06 AM
# Copyright (C) European XFEL GmbH Hamburg. All rights reserved.
#############################################################################
from asyncio import TimeoutError, wait_for

from karabo.middlelayer import (
    AccessMode, Bool, Configurable, Double, Node, State, String, Unit,
    background, sleep, Slot
)
from karabo.middlelayer_api.utils import get_property
from scpiml import ScpiAutoDevice, ScpiConfigurable

from ._version import version as deviceVersion

CONNECTION_TIMEOUT = 10  # in seconds

class ChannelNode(ScpiConfigurable):

    # def __init__(self, id):
    #     super().__init__(self)
    #     self.channelID = id

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
        description={"Output amplitude for the specified channel."})
    amplitude.poll = 10
    amplitude.readOnConnect = True

    amplitude_unit = String(
        displayedName='Amplitude Unit',
        alias='SOURce{channel_no}:VOLT:UNIT',
        options={'VPP', 'VRMS', 'DBM'},
        description={"Units of output amplitude for the specified channel."},
        defaultValue='VPP')
    amplitude_unit.readOnConnect = True

    output_state = String(
        displayedName='Output state',
        alias='OUTPut{channel_no}',
        options={'ON', 'OFF'},
        description={"Enable the AFG output for the specified channel."},
        defaultValue='OFF')
    output_state.readOnConnect = True

    def setter(self, value):
        # convert any answer to string in case of a number
        if value == 1 or '1':
            self.output_state = 'ON'
        if value == 0 or '0':
            self.output_state = 'OFF'
        else:
            self.output_state = value

    output_state.__set__ = setter


class FunctionGenerator(ScpiAutoDevice):
    __version__ = deviceVersion

    async def sendCommand(self, descriptor, value=None, child=None):
        """Redefinition of the the send and read command coros from the SCPI
        base. This is done because the Keithley does not reply on commands.
        We therefore send a command, and then query it straight away."""
        if not self.connected:
            return

        async def readCommandResult():
            return None

        descriptor = getattr(descriptor, "descriptor", descriptor)
        cmd = self.createCommand(descriptor, value)
        print("SENDING:", cmd)
        await self.writeread(cmd, readCommandResult())
        await self.sendQuery(descriptor, self)

    identification = String(
        displayedName='Identification',
        accessMode=AccessMode.READONLY,
        alias='*IDN',
        description={"Identification information on the AFG."})
    identification.readOnConnect = True

    channel_1 = Node(ChannelNode, displayedName='channel 1', alias="1")
    channel_2 = Node(ChannelNode, displayedName='channel 2', alias="2")

    def createChildQuery(self, descr, child):
        scpi_add = child.alias.format(channel_no=descr.alias)
        return f"{scpi_add}?\n"

    def createChildCommand(self, descr, value, child):
        scpi_add = child.alias.format(channel_no=descr.alias)
        return f"{scpi_add} {value.value}\n"

    amplitude2 = Double(
        displayedName='Amplitude2',
        alias='SOURce1:VOLT:AMPL',
        description={""})
    amplitude2.poll = 10
    amplitude2.readOnConnect = True

    #async def _run(self, **kwargs):
    #    self.channel_1.parent = self  # I have not found a way around this, yet
    #    await super()._run(**kwargs)
    #
    # channel_1.amplitude.poll = 10
    # channel_1.amplitude.readOnConnect = True

    pulse_width = Double(
        displayedName='Pulse width',
        unitSymbol=Unit.SECOND,
        alias='SOURce1:PULS:WIDT',
        description={"Pulse width for the specified channel."})
    pulse_width.readOnConnect = True

    burst_state = String(
        displayedName='Burst State',
        alias='SOURce1:BURSt:STAT',
        options={'ON', 'OFF'},
        description={"Enables or disables the burst mode for the "
                     "specified channel."},
        defaultValue='OFF')
    burst_state.readOnConnect = True

    def setter(self, value):
        # convert any answer to string in case of a number
        if value == 1 or '1':
            self.burst_state = 'ON'
        if value == 0 or '0':
            self.burst_state = 'OFF'
        else:
            self.burst_state = value

    burst_state.__set__ = setter

    burst_idle = String(
        displayedName='Burst Idle',
        description='Idle state means the output level between two '
                    'burst output. '
                    'START: The output keep same as the first point of '
                    'burst waveform.'
                    'DC: The output keep the DC.'
                    'END: The output keep same as the end point of burst '
                    'waveform.',
        alias='SOURce1:BURSt:IDLE',
        options={'START', 'DC', 'END', 'OFF'},
        defaultValue='OFF')
    burst_idle.readOnConnect = True

    burst_mode = String(
        displayedName='Burst Mode',
        alias='SOURce1:BURSt:MODE',
        options={'TRIG', 'GAT'},
        description={"TRIG: Means that triggered mode is selected for "
                     "burst mode."
                     "GAT: Means gated mode is selected for burst mode."},
        defaultValue='TRIG')
    burst_mode.readOnConnect = True

    burst_cycles = String(
        displayedName='Burst Cycles',
        alias='SOURce1:BURSt:NCYC',
        description={"Number of cycles (burst count) to be output in burst "
                     "mode for the specified channel. The query command "
                     "returns 9.9E+37 if the burst count is set to INFinity."
                     "Choose a number between 1 and 1,000,000 or "
                     "INF, MIN or MAX"},
        defaultValue='INF')
    burst_cycles.readOnConnect = True

    def setter(self, value):
        # convert any answer to string in case of a number
        self.burst_cycles = str(value)

    burst_cycles.__set__ = setter

    burst_delay = String(
        displayedName='Burst Delay',
        unitSymbol=Unit.SECOND,
        alias='SOURce1:BURS:TDEL',
        description={"Specifies a time delay between the trigger and the "
                     "signal output. This command is available only in the "
                     "Triggered burst mode. "
                     "The setting range is 0.0 ns to 85.000 s with "
                     "resolution of 100 ps or 5 digits."
                     "Choose a number in range or MIN or MAX"},
        defaultValue='MIN')
    burst_delay.readOnConnect = True

    def setter(self, value):
        # convert any answer to string in case of a number
        self.burst_delay = str(value)

    burst_delay.__set__ = setter

    frequency_start = Double(
        displayedName='Start Frequency',
        unitSymbol=Unit.HERTZ,
        alias='SOURce1:FREQ:STAR',
        description={"Start frequency of sweep for the specified channel. "
                     "This command is always used with the "
                     "[SOURce[1|2]]:FREQuency:STOP command. The setting "
                     "range of start frequency depends on the waveform "
                     "selected for sweep."})
    frequency_start.readOnConnect = True

    frequency_stop = Double(
        displayedName='Stop Frequency',
        unitSymbol=Unit.HERTZ,
        alias='SOURce1:FREQ:STOP',
        description={"Stop frequency of sweep for the specified channel. "
                     "This command is always used with the "
                     "[SOURce[1|2]]:FREQuency:STARt command. The setting "
                     "range of stop frequency depends on the waveform "
                     "selected for sweep."})
    frequency_stop.readOnConnect = True

    sweep_time = Double(
        displayedName='Sweep Time',
        unitSymbol=Unit.SECOND,
        alias='SOURce1:SWE:TIME',
        description={"Sweep time for the sweep for the specified channel. "
                     "The sweep time does not include hold time and return "
                     "time. The setting range is 1 ms to 500 s."})
    sweep_time.readOnConnect = True

    sweep_hold_time = Double(
        displayedName='Sweep Hold Time',
        unitSymbol=Unit.SECOND,
        alias='SOURce1:SWE:HTIM',
        description={"Sweep hold time. Hold time represents the amount of "
                     "time that the frequency must remain stable after "
                     "reaching the stop frequency."})
    sweep_hold_time.readOnConnect = True

    sweep_return_time = Double(
        displayedName='Sweep Return Time',
        unitSymbol=Unit.SECOND,
        alias='SOURce1:SWE:RTIM',
        description={"Sweep return time. Return time represents the amount "
                     "of time from stop frequency through start frequency. "
                     "Return time does not include hold time."})
    sweep_return_time.readOnConnect = True

    sweep_mode = String(
        displayedName='Sweep Mode',
        alias='SOURce1:SWE:MODE',
        options={'AUTO', 'MAN'},
        description={"AUTO: Sets the sweep mode to auto; the instrument "
                     "outputs a continuous sweep at a rate specified by "
                     "Sweep Time, Hold Time, and Return Time."
                     "MAN: Sets the sweep mode to manual; the instrument "
                     "outputs one sweep when a trigger input is received."},
        defaultValue='AUTO')
    sweep_mode.readOnConnect = True

    # CHANNEL independent parameters
    trigger_mode = String(
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
    trigger_mode.readOnConnect = True

    trigger_source = String(
        displayedName='Trigger Source',
        alias='TRIG:SOUR',
        options={'TIM', 'EXT'},
        description={"TIM: Specifies an internal clock as the trigger "
                     "source. EXT: use external trigger source"},
        defaultValue='TIM')
    trigger_source.readOnConnect = True

    trigger_time = Double(
        displayedName='Trigger Time',
        alias='TRIG:TIM',
        unitSymbol=Unit.SECOND,
        description={"Period of an internal clock when you select the "
                     "internal clock as the trigger source. "
                     "The setting range is 1 μs to 500.0 s."},
        defaultValue=10)
    trigger_time.readOnConnect = True

    run_mode = String(
        displayedName='Run Mode',
        alias='SEQC:RMOD',
        options={'CONT', 'TRIG', 'GAT', 'SEQ'},
        description={"CONT: Sets Run Mode to Continuous."
                     "TRIG: Sets Run Mode to Triggered."
                     "GAT: Sets Run Mode to Gated."
                     "SEQ: Sets Run Mode to Sequence."},
        defaultValue='CONT')
    run_mode.readOnConnect = True

    # @Slot(
    #     displayedName="Connect",
    #     allowedStates=[State.UNKNOWN]
    # )
    # async def connect(self):
    #     self.state = State.CHANGING
    #     self.status = "Connecting..."
    #     if self.connect_task:
    #         self.connect_task.cancel()
    #     self.connect_task = background(self._connect())
    #
    # async def _connect(self):
    #     """Connects to the instrument.
    #
    #     In case of failures the state is set to UNKNOWN and the device tries
    #     to reconnect.
    #     """
    #     msg = ""
    #     try:
    #         await wait_for(super().connect(), timeout=CONNECTION_TIMEOUT)
    #     except TimeoutError as e:
    #         if "Timeout while waiting for reply" not in str(e):
    #             msg = (f"Error: Timeout ({CONNECTION_TIMEOUT} s) in "
    #                    "connecting to the Keithley instrument. Please, "
    #                    "fix the problem and reconnect to the instrument.")
    #     except ConnectionRefusedError as e:
    #         msg = ("Error: ConnectionRefused with the Keithley instrument. "
    #                f"Exception: {e}. Please, fix the problem and "
    #                "reconnect to the instrument.")
    #     finally:
    #         # dump a message in case of error and re-try connecting
    #         if msg:
    #             if self.status != msg:
    #                 self.logger.error(msg)
    #                 self.status = msg
    #                 self.state = State.UNKNOWN
    #             self.connect_task = background(self._connect())
    #             return False
    #
    #     self.status = "Connected"
    #
    #     return True

    async def onInitialization(self):
        self.initialized = True
    #    self.connect_task = None


    # async def onDestruction(self):
    #     """Actions to take when the device is shutdown."""
    #     if self.connect_task:  # connecting
    #         self.connect_task.cancel()
    #     await super().onDestruction()