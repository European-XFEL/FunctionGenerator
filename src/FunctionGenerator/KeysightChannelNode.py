from karabo.middlelayer import (
    AccessLevel, AccessMode, Double, Slot, State, String, Unit
)

from .FunctionGenerator import ChannelNodeBase


class KeysightChannelNode(ChannelNodeBase):

    outputLoad = Double(
        displayedName='Output Load',
        alias='OUTPut{channel_no}:LOAD',
        description="Sets expected output termination.")

    func_shape_dict = {'SIN': 'Sine',
                       'SQU': 'Square',
                       'RAMP': 'Ramp',
                       'TRI': 'Triangle',
                       'PULS': 'Pulse',
                       'NOIS': 'Noise',
                       'PRBS': 'PRBS',
                       'ARB': 'Arbitrary',
                       'DC': 'DC'}

    functionShape = String(
        displayedName='Function Shape',
        alias='SOURce{channel_no}:FUNCtion',
        options=list(func_shape_dict.values()),
        description="Selects the output function",
        defaultValue='Sine')

    def setter(self, value):
        value = str(value)
        if value in self.func_shape_dict.keys():
            value = self.func_shape_dict[value]
        try:
            self.functionShape = value
        except ValueError:
            self.status = f"Function shape return value {value} not one " \
                          f"of the valid options"

    functionShape.__set__ = setter

    pulseWidth = Double(
        displayedName='Pulse Width',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:FUNC:PULS:WIDT',
        description="Pulse width is the time from the 50% threshold of a "
                    "pulse's rising edge to the 50% threshold of the next "
                    "falling edge.")
    pulseWidth.poll = True

    pulsePeriod = Double(
        displayedName='Pulse Period',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:FUNC:PULS:PER',
        description="Period of pulse waveform.")
    pulsePeriod.poll = True

    pulseLeadingEdge = Double(
        displayedName='Pulse Leading Edge',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:FUNC:PULS:TRAN:LEAD',
        description="Pulse leading edge time.")
    pulseLeadingEdge.poll = True

    pulseTrailingEdge = Double(
        displayedName='Pulse Trailing Edge',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:FUNC:PULS:TRAN:TRA',
        description="Pulse trailing edge time.")
    pulseTrailingEdge.poll = True

    burstPeriod = Double(
        displayedName='Burst Period',
        alias='SOURce{channel_no}:BURSt:INTernal:PERiod',
        description="Burst period for internally-triggered bursts.")
    burstPeriod.poll = True

    sweepState = String(
        displayedName='Sweep State',
        alias='SOURce{channel_no}:SWE:STAT',
        options={'ON', 'OFF'},
        description="Enables or disables the sweep mode for the "
                    "specified channel.",
        defaultValue='OFF')
    sweepState.poll = True

    def setter(self, value):
        # convert any answer to string in case of a number
        try:
            if value == 0 or value == '0' or value == "OFF":
                self.sweepState = 'OFF'
            elif value != 0 or value == '1' or value == "ON":
                self.sweepState = 'ON'
            else:
                self.sweepState = str(value)

        except ValueError:
            self.status = f"Sweep state return value {value} not one " \
                          "of the valid options"

    sweepState.__set__ = setter

    arbitraryPeriod = Double(
        displayedName='Arbitrary Period',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:FUNC:ARB:PER',
        description="Period of arbitrary waveform.")

    rampSymmetry = Double(
        displayedName='Ramp Symmetry',
        alias='SOURce{channel_no}:FUNC:RAMP:SYMM',
        description="Symmetry of ramp waveform in percent.")

    triggerSource = String(
        displayedName='Trigger Source',
        alias='TRIG{channel_no}:SOUR',
        options={'TIM', 'EXT', "BUS", "IMM"},
        description="Selects the trigger source. Immediate or timed internal "
                    "trigger, external or software (BUS) trigger.",
        defaultValue='TIM')

    triggerTime = Double(
        displayedName='Trigger Time',
        alias='TRIG{channel_no}:TIM',
        unitSymbol=Unit.SECOND,
        description="Period of an internal clock when you select the "
                    "internal clock as the trigger source.",
        defaultValue=10)

    # The following properties should not be used directly but are internally
    # used in slots to trigger scpiML response

    selectArbForm = String(
        displayedName='Select Arbitrary Form',
        alias='SOURce{channel_no}:FUNC:ARB',
        description="Select arbitrary waveform in memory.",
        requiredAccessLevel=AccessLevel.EXPERT)
    selectArbForm.readOnConnect = False
    selectArbForm.commandReadBack = False

    loadArbForm = String(
        displayedName='Load Arbitrary Form',
        alias='MMEMory:LOAD:DATA{channel_no}',
        description="Load file with arbitrary waveform.",
        requiredAccessLevel=AccessLevel.EXPERT)
    loadArbForm.readOnConnect = False
    loadArbForm.commandReadBack = False

    # now the interface to the user for the above parameters

    lastSelectArb = String(
        displayedName='Last Selected Arbitrary Form',
        accessMode=AccessMode.READONLY)

    lastLoadedArb = String(
        displayedName='Last Loaded Arbitrary Form',
        accessMode=AccessMode.READONLY)

    @Slot(displayedName="Select Arbitrary Waveform",
          allowedStates=[State.NORMAL])
    async def selectArb(self):
        # make sure function shape is set to ARB otherwise hardware
        # behaves strange and gets stuck in timeouts
        descr = getattr(self.__class__, "functionShape")
        await descr.setter(self, "Arbitrary")
        descr = getattr(self.__class__, "selectArbForm")
        arb = self.get_root().availableArbs.value
        # {chr(92)} represents backlash so flake8 does not complain
        await descr.setter(self, f'"INT:{chr(92)}BUILTIN{chr(92)}{arb}"')
        self.lastSelectArb = arb

    @Slot(displayedName="Load Arbitrary Waveform",
          allowedStates=[State.NORMAL])
    async def loadArb(self):
        descr = getattr(self.__class__, "loadArbForm")
        arb = self.get_root().availableArbs.value
        # {chr(92)} represents backlash so flake8 does not complain
        await descr.setter(self, f'"INT:{chr(92)}BUILTIN{chr(92)}{arb}"')
        self.lastLoadedArb = arb
