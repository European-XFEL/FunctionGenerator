#############################################################################
# Author: amunnich
# Created on April 04, 2022, 11:06 AM
# Copyright (C) European XFEL GmbH Hamburg. All rights reserved.
#############################################################################
from asyncio import wait_for
from karabo.middlelayer import (
    AccessLevel, Overwrite, Slot, State, String
)

from .FunctionGenerator import FunctionGenerator


class KeysightBase(FunctionGenerator):

    phaseUnit = String(
        displayedName='Phase Unit',
        alias='UNIT:ANGLe',
        options={'DEG', 'RAD'},
        defaultValue="DEG",
        description="Unit of Phase offset angle of waveform.")

    arbPath = String(
        displayedName='Waveform Paths',
        description="File paths for arbitrary waveforms. ",
        defaultValue=r'INT:\BUILTIN')

    @Slot(displayedName="Get Arbitrary Waveforms",
          allowedStates=[State.NORMAL])
    async def getArbs(self):
        descr = getattr(self.__class__, "arbs")
        # path needs explicit quotations when send to hardware
        await descr.setter(self, f'"{self.arbPath}"')
        if self.arb_options:
            setattr(self.__class__, 'availableArbs',
                    Overwrite(options=self.arb_options,
                              defaultValue=self.arb_options[0]))
            await self.publishInjectedParameters()

    # options will be filled after connect when read from hardware
    arb_options = None

    availableArbs = String(
        displayedName='Available Arbitrary Waveforms',
        description="Available arbitrary waveforms on the hardware.",
        options=arb_options)

    display = String(
        displayedName='Display',
        alias='DISPlay',
        options={'ON', 'OFF'},
        defaultValue='OFF',
        description="Turn Display on or off. OFF on start of device. "
                    "Control on hardware side can be reclaimed by pressing "
                    "the 'Local' key")
    display.writeOnConnect = True
    display.commandReadBack = True

    def setter(self, value):
        # convert any answer to string in case of a number
        try:
            if value == 0 or value == '0' or value == "OFF":
                self.display = 'OFF'
            elif value != 0 or value == '1' or value == "ON":
                self.display = 'ON'
            else:
                self.status = f"Unknown value received for Display: {value}"

        except ValueError:
            self.status = f"Display return value {value} not one " \
                          "of the valid options"

    display.__set__ = setter

    arbs = String(
        displayedName='Request Arbs',
        alias='MMEMory:CAT:DATA:ARB',
        defaultValue=r'INT:\BUILTIN',
        description="Request available arbitrary waveforms.",
        requiredAccessLevel=AccessLevel.EXPERT)
    arbs.commandFormat = '{alias}? {value}\n'
    arbs.commandReadBack = False
    arbs.readOnConnect = False

    def setter(self, value):
        self.arb_options = [a.strip('"') for a in value.split(",")
                            if ".arb" in a]

    arbs.__set__ = setter

    # overwriting connect so options can be set after reading values
    # from hardware
    async def connect(self):
        await wait_for(super().connect(), timeout=5)
        await self.getArbs()
