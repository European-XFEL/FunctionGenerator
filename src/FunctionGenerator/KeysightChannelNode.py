from asyncio import sleep
from karabo.middlelayer import (
    Double, String, Unit
)

from .FunctionGenerator import ChannelNodeBase


class KeysightChannelNode(ChannelNodeBase):

    outputLoad = Double(
        displayedName='Output load',
        alias='OUTPut{channel_no}:LOAD',
        description={"Sets expected output termination.."})
    outputLoad.readOnConnect = True
    outputLoad.commandReadBack = True

    functionShape = String(
        displayedName='Function Shape',
        alias='SOURce{channel_no}:FUNCtion',
        options={'SIN', 'SQU', 'RAMP', 'NRAM', 'TRI', 'PULS', 'NOIS',
                 'PRBS', 'ARB', 'DC'},
        description={"Selects the output function"},
        defaultValue='SIN')
    functionShape.readOnConnect = True
    functionShape.commandReadBack = True

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
    pulseWidth.commandReadBack = True
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
            # TODO: code gets here but status is not shown in GUI, try this:
            await sleep(1)
        else:
            self.pulseWidth = value

    pulseWidth.__set__ = setter

    pulsePeriod = Double(
        displayedName='Pulse period',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:FUNC:PULS:PER',
        description={"Period of pulse waveform."})
    pulsePeriod.readOnConnect = True
    pulsePeriod.commandReadBack = True
    pulsePeriod.commandFormat = "{alias} {value} s"

    arbitraryForm = String(
        displayedName='Select Arbitrary Form',
        alias='SOURce{channel_no}:FUNC:ARB',
        description={"Select arbitrary waveform in memory."})

    loadForm = String(
        displayedName='Load Arbitrary Form',
        alias='MMEMory:LOAD:DATA{channel_no}',
        description={"Load file with arbitrary waveform."})

    arbitraryPeriod = Double(
        displayedName='Arbitrary period',
        unitSymbol=Unit.SECOND,
        alias='SOURce{channel_no}:FUNC:ARB:PER',
        description={"Period of arbitrary waveform."})
    arbitraryPeriod.readOnConnect = True
    arbitraryPeriod.commandReadBack = True
    arbitraryPeriod.commandFormat = "{alias} {value} s"

    rampSymmetry = Double(
        displayedName='Ramp Symmetry',
        alias='SOURce{channel_no}:FUNC:RAMP:SYMM',
        description={"Symmetry of ramp waveform in percent."})
    rampSymmetry.readOnConnect = True
    rampSymmetry.commandReadBack = True
    rampSymmetry.commandFormat = "{alias} {value} s"

    triggerSource = String(
        displayedName='Trigger Source',
        alias='TRIG{channel_no}:SOUR',
        options={'TIM', 'EXT', "BUS", "IMM"},
        description={"Selects the trigger source. Immediate or timed internal "
                     "trigger, external or software (BUS) trigger."},
        defaultValue='TIM')
    triggerSource.readOnConnect = True
    triggerSource.commandReadBack = True

    triggerTime = Double(
        displayedName='Trigger Time',
        alias='TRIG{channel_no}:TIM',
        unitSymbol=Unit.SECOND,
        description={"Period of an internal clock when you select the "
                     "internal clock as the trigger source."},
        defaultValue=10)
    triggerTime.readOnConnect = True
    triggerTime.commandReadBack = True
    triggerTime.commandFormat = "{alias} {value} s"