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
from scpiml import ScpiAutoDevice

from ._version import version as deviceVersion

CONNECTION_TIMEOUT = 10  # in seconds

class ChannelNode(Configurable):

    # def __init__(self, id):
    #     super().__init__(self)
    #     self.channelID = id

    functionShape = String(
        displayedName='Function Shape',
        alias='SOURce1:FUNCtion:SHAPe',
        options={'SIN', 'SQU', 'PULS', 'RAMP', 'PRN', 'DC', 'SINC', 'GAUS',
                 'LOR', 'ERIS', 'EDEC', 'EMEM'},
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
        alias='SOURce1:VOLT:OFFS')
    offset.readOnConnect = True
    offset.poll = 10

    amplitude = Double(
        displayedName='Amplitude',
        alias='SOURce1:VOLT:AMPL')
    amplitude.poll = 10
    amplitude.readOnConnect = True

    amplitude_unit = String(
        displayedName='Amplitude Unit',
        alias='SOURce1:VOLT:UNIT',
        options={'VPP', 'VRMS', 'DBM'},
        defaultValue='VPP')
    amplitude_unit.readOnConnect = True

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
        alias='*IDN')
    identification.readOnConnect = True

    channel_1 = Node(ChannelNode, displayedName='channel 1')

    amplitude2 = Double(
        displayedName='Amplitude2',
        alias='SOURce1:VOLT:AMPL')
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
        alias='SOURce1:PULS:WIDT')
    pulse_width.readOnConnect = True

    burst_state = String(
        displayedName='Burst State',
        alias='SOURce1:BURSt:STAT',
        options={'ON', 'OFF'},
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
        defaultValue='TRIG')
    burst_mode.readOnConnect = True

    burst_cycles = String(
        displayedName='Burst Cycles',
        alias='SOURce1:BURSt:NCYC',
        defaultValue='INF')
    burst_cycles.readOnConnect = True

    def setter(self, value):
        # convert any answer to string in case of a number
        self.burst_cycles = str(value)

    burst_cycles.__set__ = setter

    burst_delay = Double(
        displayedName='Burst Delay',
        unitSymbol=Unit.SECOND,
        alias='SOURce1:BURS:TDEL')
    burst_delay.readOnConnect = True

    frequency_start = Double(
        displayedName='Start Frequency',
        unitSymbol=Unit.HERTZ,
        alias='SOURce1:FREQ:STAR')
    frequency_start.readOnConnect = True

    frequency_stop = Double(
        displayedName='Stop Frequency',
        unitSymbol=Unit.HERTZ,
        alias='SOURce1:FREQ:STOP')
    frequency_stop.readOnConnect = True

    sweep_time = Double(
        displayedName='Sweep Time',
        unitSymbol=Unit.SECOND,
        alias='SOURce1:SWE:TIME')
    sweep_time.readOnConnect = True

    sweep_hold_time = Double(
        displayedName='Sweep Hold Time',
        unitSymbol=Unit.SECOND,
        alias='SOURce1:SWE:HTIM')
    sweep_hold_time.readOnConnect = True

    sweep_return_time = Double(
        displayedName='Sweep Return Time',
        unitSymbol=Unit.SECOND,
        alias='SOURce1:SWE:RTIM')
    sweep_return_time.readOnConnect = True

    sweep_mode = String(
        displayedName='Sweep Mode',
        alias='SOURce1:SWE:MODE',
        options={'AUTO', 'MAN'},
        defaultValue='AUTO')
    sweep_mode.readOnConnect = True

    output_state = String(
        displayedName='Output state',
        alias='OUTPut1',
        options={'ON', 'OFF'},
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

    # CHANNEL independent parameters
    trigger_mode = String(
        displayedName='Trigger Mode',
        alias='OUTP:TRIG:MODE',
        options={'TRIG', 'SYNC'},
        defaultValue='TRIG')
    trigger_mode.readOnConnect = True

    trigger_source = String(
        displayedName='Trigger Source',
        alias='TRIG:SOUR',
        options={'TIM', 'EXT'},
        defaultValue='TIM')
    trigger_source.readOnConnect = True

    trigger_time = Double(
        displayedName='Trigger Time',
        alias='TRIG:TIM',
        unitSymbol=Unit.SECOND,
        defaultValue=10)
    trigger_time.readOnConnect = True

    run_mode = String(
        displayedName='Run Mode',
        alias='SEQC:RMOD',
        options={'CONT', 'TRIG', 'GAT', 'SEQ'},
        defaultValue='CONT')
    run_mode.readOnConnect = True

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
                msg = (f"Error: Timeout ({CONNECTION_TIMEOUT} s) in "
                       "connecting to the Keithley instrument. Please, "
                       "fix the problem and reconnect to the instrument.")
        except ConnectionRefusedError as e:
            msg = ("Error: ConnectionRefused with the Keithley instrument. "
                   f"Exception: {e}. Please, fix the problem and "
                   "reconnect to the instrument.")
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


    async def onDestruction(self):
        """Actions to take when the device is shutdown."""
        if self.connect_task:  # connecting
            self.connect_task.cancel()
        await super().onDestruction()