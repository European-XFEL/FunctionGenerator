from karabo.middlelayer import (
    Double, String, Unit
)

from .FunctionGenerator import ChannelNodeBase


class KeysightChannelNode(ChannelNodeBase):

    outputLoad = Double(
        displayedName='Output Load',
        alias='OUTPut{channel_no}:LOAD',
        description="Sets expected output termination.")
    outputLoad.readOnConnect = True
    outputLoad.commandReadBack = True

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
    functionShape.readOnConnect = True
    functionShape.commandReadBack = True

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
    pulseWidth.readOnConnect = True
    pulseWidth.commandReadBack = True

    def setter(self, value):
        #  check if value in allowed range for period set
        if not self.pulsePeriod:
            self.pulseWidth = value
            return
        elif value > self.pulsePeriod.value:
            raise ValueError(f"Invalid value for pulseWidth: {value}. "
                             f"Has to be smaller than the "
                             f"period {self.pulsePeriod.value}")
        else:
            self.pulseWidth = value

    pulseWidth.__set__ = setter

    pulsePeriod = Double(
        displayedName='Pulse Period',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:FUNC:PULS:PER',
        description="Period of pulse waveform.")
    pulsePeriod.readOnConnect = True
    pulsePeriod.commandReadBack = True

    arbitraryForm = String(
        displayedName='Select Arbitrary Form',
        alias='SOURce{channel_no}:FUNC:ARB',
        description="Select arbitrary waveform in memory.")

    loadForm = String(
        displayedName='Load Arbitrary Form',
        alias='MMEMory:LOAD:DATA{channel_no}',
        description="Load file with arbitrary waveform.")

    arbitraryPeriod = Double(
        displayedName='Arbitrary Period',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:FUNC:ARB:PER',
        description="Period of arbitrary waveform.")
    arbitraryPeriod.readOnConnect = True
    arbitraryPeriod.commandReadBack = True

    rampSymmetry = Double(
        displayedName='Ramp Symmetry',
        alias='SOURce{channel_no}:FUNC:RAMP:SYMM',
        description="Symmetry of ramp waveform in percent.")
    rampSymmetry.readOnConnect = True
    rampSymmetry.commandReadBack = True

    triggerSource = String(
        displayedName='Trigger Source',
        alias='TRIG{channel_no}:SOUR',
        options={'TIM', 'EXT', "BUS", "IMM"},
        description="Selects the trigger source. Immediate or timed internal "
                    "trigger, external or software (BUS) trigger.",
        defaultValue='TIM')
    triggerSource.readOnConnect = True
    triggerSource.commandReadBack = True

    triggerTime = Double(
        displayedName='Trigger Time',
        alias='TRIG{channel_no}:TIM',
        unitSymbol=Unit.SECOND,
        description="Period of an internal clock when you select the "
                    "internal clock as the trigger source.",
        defaultValue=10)
    triggerTime.readOnConnect = True
    triggerTime.commandReadBack = True
