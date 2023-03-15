#############################################################################
# Author: amunnich
# Created on April 04, 2022, 11:06 AM
# Copyright (C) European XFEL GmbH Hamburg. All rights reserved.
#############################################################################

from karabo.middlelayer import (
    Assignment, Double, Node, String, Unit
)

from .FunctionGenerator import FunctionGenerator, ChannelNodeBase


class AFGChannelNode(ChannelNodeBase):

    func_shape_dict = {'SIN': 'Sine',
                       'SQU': 'Square',
                       'RAMP': 'Ramp',
                       'PULS': 'Pulse',
                       'PRN': 'PR Noise',
                       'SINC': 'Sin(x)/x',
                       'GAUS': 'Gaussian',
                       'DC': 'DC',
                       'LOR': 'Lorentz',
                       'ERIS': 'Exponential Rise',
                       'EDEC': 'Exponential Decay',
                       'HAV': 'Haversine'}

    functionShape = String(
        displayedName='Function Shape',
        alias='SOURce{channel_no}:FUNCtion',
        options=list(func_shape_dict.values()),
        description="Shape of the output waveform. When the specified user "
                    "memory is deleted, this command causes an error if you "
                    "select the user memory. "
                    "If you select a waveform shape that is not allowed with "
                    "a particular modulation, sweep, or burst, Run mode "
                    "automatically changes to Continuous.",
        defaultValue='Pulse',
        # TODO default not needed for Assignment.INTERNAL if Karabo >= 2.16.3
        assignment=Assignment.INTERNAL)

    def func_setter(self, value):
        value = str(value)
        if value in self.func_shape_dict.keys():
            value = self.func_shape_dict[value]
        try:
            self.functionShape = value
        except ValueError:
            self.status = f"Function shape return value {value} not one " \
                          f"of the valid options"

    functionShape.__set__ = func_setter

    pulseWidth = Double(
        displayedName='Pulse Width',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:PULS:WIDT',
        description="Pulse Width = Period * Duty Cycle / 100. "
                    "The pulse width must be less than the period. "
                    "The setting range is 0.001% to 99.999% in terms of "
                    "duty cycle.",
        defaultValue=0.,
        # TODO default not needed for Assignment.INTERNAL if Karabo >= 2.16.3
        assignment=Assignment.INTERNAL)
    pulseWidth.commandFormat = "{alias} {value} s"
    pulseWidth.poll = True

    pulsePeriod = Double(
        displayedName='Pulse Period',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:PULS:PER',
        description="Period of pulse waveform.",
        defaultValue=0.,
        # TODO default not needed for Assignment.INTERNAL if Karabo >= 2.16.3
        assignment=Assignment.INTERNAL)
    pulsePeriod.commandFormat = "{alias} {value} s"
    pulsePeriod.poll = True

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
        defaultValue='OFF',
        # TODO default not needed for Assignment.INTERNAL if Karabo >= 2.16.3
        assignment=Assignment.INTERNAL)

    burstDelay = String(
        displayedName='Burst Delay',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:BURS:TDEL',
        description={"Specifies a time delay between the trigger and the "
                     "signal output. This command is available only in the "
                     "Triggered burst mode. "
                     "The setting range is 0.0 ns to 85.000 s with "
                     "resolution of 100 ps or 5 digits. "
                     "Choose a number in range or MIN or MAX."},
        defaultValue='MIN',
        # TODO default not needed for Assignment.INTERNAL if Karabo >= 2.16.3
        assignment=Assignment.INTERNAL)
    burstDelay.commandFormat = "{alias} {value} s"

    sweepMode = String(
        displayedName='Sweep Mode',
        alias='SOURce{channel_no}:SWE:MODE',
        options={'AUTO', 'MAN'},
        description="AUTO: Sets the sweep mode to auto; the instrument "
                    "outputs a continuous sweep at a rate specified by "
                    "Sweep Time, Hold Time, and Return Time. "
                    "MAN: Sets the sweep mode to manual; the instrument "
                    "outputs one sweep when a trigger input is received.",
        defaultValue='AUTO',
        # TODO default not needed for Assignment.INTERNAL if Karabo >= 2.16.3
        assignment=Assignment.INTERNAL)


class AFG31000(FunctionGenerator):

    channel_1 = Node(AFGChannelNode, displayedName='channel 1', alias="1")
    channel_2 = Node(AFGChannelNode, displayedName='channel 2', alias="2")

    # CHANNEL independent parameters
    triggerMode = String(
        displayedName='Trigger Mode',
        alias='OUTP:TRIG:MODE',
        options={'TRIG', 'SYNC'},
        description="The mode (trigger or sync) for Trigger Output signal. "
                    "When the burst count is set to Inf-Cycles in burst mode,"
                    "TRIGger indicates that the infinite number of cycles "
                    "of waveform will be output from the Trigger Output "
                    "connector. When the burst count is set to Inf-Cycles "
                    "in burst mode, SYNC indicates that one pulse waveform "
                    "is output from the Trigger Output connector when the "
                    "Inf-Cycles starts. When Run Mode is specified other "
                    "than Burst Inf-Cycles, TRIGger, and SYNC have the "
                    "same effect.",
        defaultValue='TRIG',
        # TODO default not needed for Assignment.INTERNAL if Karabo >= 2.16.3
        assignment=Assignment.INTERNAL)

    triggerSource = String(
        displayedName='Trigger Source',
        alias='TRIG:SOUR',
        options={'TIM', 'EXT'},
        description="TIM: Specifies an internal clock as the trigger "
                    "source. EXT: use external trigger source.",
        defaultValue='TIM',
        # TODO default not needed for Assignment.INTERNAL if Karabo >= 2.16.3
        assignment=Assignment.INTERNAL)

    triggerTime = Double(
        displayedName='Trigger Time',
        alias='TRIG:TIM',
        unitSymbol=Unit.SECOND,
        description="Period of an internal clock when you select the "
                    "internal clock as the trigger source.",
        defaultValue=10,
        # TODO default not needed for Assignment.INTERNAL if Karabo >= 2.16.3
        minInc=1e-6,
        maxInc=500.0,
        assignment=Assignment.INTERNAL)
    triggerTime.commandFormat = "{alias} {value} s"

    runMode = String(
        displayedName='Run Mode',
        alias='SEQC:RMOD',
        options={'CONT', 'TRIG', 'GAT', 'SEQ'},
        description="CONT: Sets Run Mode to Continuous. "
                    "TRIG: Sets Run Mode to Triggered. "
                    "GAT: Sets Run Mode to Gated. "
                    "SEQ: Sets Run Mode to Sequence.",
        defaultValue='CONT',
        # TODO default not needed for Assignment.INTERNAL if Karabo >= 2.16.3
        assignment=Assignment.INTERNAL)
    runMode.poll = True

    lock = String(
        displayedName='Lock',
        alias='SYST:KLOCk',
        options={'ON', 'OFF'},
        defaultValue='ON',
        description="Lock hardware from local use while remote operation "
                    "in progress. ON on start of device.")
    lock.readOnConnect = False
    lock.writeOnConnect = True
    lock.commandReadBack = True

    def lock(self, value):
        if value == 0 or value == '0' or value == "OFF":
            self.lock = "OFF"
        else:
            self.lock = "ON"

    lock.__set__ = lock
