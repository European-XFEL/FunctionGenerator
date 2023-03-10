from karabo.middlelayer import (
    AccessLevel, AccessMode, Assignment, Double, Slot, State, String,
    Unit, VectorString
)

from .FunctionGenerator import ChannelNodeBase


class KeysightChannelNode(ChannelNodeBase):

    outputLoad = Double(
        displayedName='Output Load',
        alias='OUTPut{channel_no}:LOAD',
        description="Sets expected output termination.",
        assignment=Assignment.INTERNAL)

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
        defaultValue='Sine',
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
        alias='SOURce{channel_no}:FUNC:PULS:WIDT',
        description="Pulse width is the time from the 50% threshold of a "
                    "pulse's rising edge to the 50% threshold of the next "
                    "falling edge.",
        assignment=Assignment.INTERNAL)
    pulseWidth.poll = True

    pulsePeriod = Double(
        displayedName='Pulse Period',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:FUNC:PULS:PER',
        description="Period of pulse waveform.",
        assignment=Assignment.INTERNAL)
    pulsePeriod.poll = True

    pulseLeadingEdge = Double(
        displayedName='Pulse Leading Edge',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:FUNC:PULS:TRAN:LEAD',
        description="Pulse leading edge time.",
        assignment=Assignment.INTERNAL)
    pulseLeadingEdge.poll = True

    pulseTrailingEdge = Double(
        displayedName='Pulse Trailing Edge',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:FUNC:PULS:TRAN:TRA',
        description="Pulse trailing edge time.",
        assignment=Assignment.INTERNAL)
    pulseTrailingEdge.poll = True

    burstPeriod = Double(
        displayedName='Burst Period',
        alias='SOURce{channel_no}:BURSt:INTernal:PERiod',
        description="Burst period for internally-triggered bursts.",
        assignment=Assignment.INTERNAL)
    burstPeriod.poll = True

    sweepState = String(
        displayedName='Sweep State',
        alias='SOURce{channel_no}:SWE:STAT',
        options={'ON', 'OFF'},
        description="Enables or disables the sweep mode for the "
                    "specified channel.",
        defaultValue='OFF',
        assignment=Assignment.INTERNAL)
    sweepState.poll = True

    def sweep_state_setter(self, value):
        self.on_off_setter(value, "sweepState")

    sweepState.__set__ = sweep_state_setter

    arbitraryPeriod = Double(
        displayedName='Arbitrary Period',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:FUNC:ARB:PER',
        description="Period of arbitrary waveform.",
        assignment=Assignment.INTERNAL)

    arbitraryRate = Double(
        displayedName='Arbitrary Sample Rate',
        alias='SOURce{channel_no}:FUNC:ARB:SRAT',
        description="Sample rate of arbitrary waveform.",
        assignment=Assignment.INTERNAL)

    rampSymmetry = Double(
        displayedName='Ramp Symmetry',
        alias='SOURce{channel_no}:FUNC:RAMP:SYMM',
        description="Symmetry of ramp waveform in percent.",
        assignment=Assignment.INTERNAL)

    triggerSource = String(
        displayedName='Trigger Source',
        alias='TRIG{channel_no}:SOUR',
        options={'TIM', 'EXT', "BUS", "IMM"},
        description="Selects the trigger source. Immediate or timed internal "
                    "trigger, external or software (BUS) trigger.",
        defaultValue='TIM',
        assignment=Assignment.INTERNAL)

    triggerTime = Double(
        displayedName='Trigger Time',
        alias='TRIG{channel_no}:TIM',
        unitSymbol=Unit.SECOND,
        description="Period of an internal clock when you select the "
                    "internal clock as the trigger source.",
        defaultValue=10,
        assignment=Assignment.INTERNAL)

    # The following properties should not be used directly but are internally
    # used in slots to trigger scpiML response

    selectArbForm = String(
        displayedName='Select Arbitrary Form',
        alias='SOURce{channel_no}:FUNC:ARB',
        description="Select arbitrary waveform in memory.",
        requiredAccessLevel=AccessLevel.EXPERT,
        accessMode=AccessMode.READONLY)
    selectArbForm.readOnConnect = False
    selectArbForm.commandReadBack = False

    loadArbForm = String(
        displayedName='Load Arbitrary Form',
        alias='MMEMory:LOAD:DATA{channel_no}',
        description="Load file with arbitrary waveform.",
        requiredAccessLevel=AccessLevel.EXPERT,
        accessMode=AccessMode.READONLY)
    loadArbForm.readOnConnect = False
    loadArbForm.commandReadBack = False

    catalog = String(
        displayedName='Get Catalog',
        alias='SOURce{channel_no}:DATA:VOL:CAT',
        description="Request catalog info.",
        requiredAccessLevel=AccessLevel.EXPERT,
        accessMode=AccessMode.READONLY)
    catalog.commandFormat = '{alias}?\n'
    catalog.commandReadBack = False
    catalog.readOnConnect = True

    def cat_setter(self, value):
        self.loadedArbs = [a.strip('"') for a in value.split(",")]
        # TODO: built a proper option lists to be used in select arb

    catalog.__set__ = cat_setter

    clearMem = String(
        displayedName='Clear Memory',
        alias='SOURce{channel_no}:DATA:VOL:CLEar',
        description="Clear all Loaded arbitrary waveform from memory.",
        requiredAccessLevel=AccessLevel.EXPERT,
        accessMode=AccessMode.READONLY)
    clearMem.commandFormat = '{alias}\n'
    clearMem.readOnConnect = False
    clearMem.commandReadBack = False

    # now the interface to the user for the above parameters

    # TODO: filling of options
    # selectArbForm = String(
    #     displayedName='Available Waveforms',
    #     description="Choose an available arbitrary waveform to be loaded into"
    #                 "memory. "
    #                 "Note: If you choose a sequence file, all waveforms "
    #                 "referenced in there have to be loaded first. The "
    #                 "folder structure has to be maintained.",
    #     options="")

    parent = None

    def setup(self, parent):
        self.parent = parent

    @Slot(displayedName="Select Arbitrary Waveform",
          allowedStates=[State.NORMAL])
    async def selectArb(self):
        # make sure function shape is set to ARB otherwise hardware
        # behaves strange and gets stuck in timeouts
        descr = getattr(self.__class__, "functionShape")
        await descr.setter(self, "Arbitrary")
        descr = getattr(self.__class__, "selectArbForm")
        arb = self.get_root().availableArbs.value
        await descr.setter(self, fr'"{self.parent.arbPath}\{arb.upper()}"')

    @Slot(displayedName="Load Arbitrary Waveform",
          allowedStates=[State.NORMAL])
    async def loadArb(self):
        descr = getattr(self.__class__, "loadArbForm")
        arb = self.get_root().availableArbs.value
        await descr.setter(self, fr'"{self.parent.arbPath}\{arb}"')
        # update loaded list
        await self.get_loaded_arbs()

    async def get_loaded_arbs(self):
        descr = getattr(self.__class__, "catalog")
        await descr.setter(self, "")

    @Slot(displayedName="Clear Memory",
          allowedStates=[State.NORMAL])
    async def clearMemory(self):
        descr = getattr(self.__class__, "clearMem")
        await descr.setter(self, "")
