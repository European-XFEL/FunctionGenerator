#############################################################################
# Author: amunnich
# Created on April 04, 2022, 11:06 AM
# Copyright (C) European XFEL GmbH Hamburg. All rights reserved.
#############################################################################
from asyncio import wait_for
from karabo.middlelayer import (
    AccessLevel, AccessMode, Assignment, Overwrite, Slot, State, String
)

from .FunctionGenerator import FunctionGenerator


class KeysightBase(FunctionGenerator):

    phaseUnit = String(
        displayedName='Phase Unit',
        alias='UNIT:ANGLe',
        options={'DEG', 'RAD'},
        defaultValue="DEG",
        description="Unit of Phase offset angle of waveform.",
        assignment=Assignment.INTERNAL)

    arbPath = String(
        displayedName='Waveform Paths',
        description="File paths for arbitrary waveforms. Use backslash to"
                    "separate folders. No backslash at the end!",
        defaultValue=r'INT:\BUILTIN')

    @Slot(displayedName="Get Waveforms",
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
        displayedName='Available Waveforms',
        description="Available arbitrary waveforms on the hardware. "
                    "Note: If you choose a sequence file, all waveforms "
                    "referenced in there have to be loaded first. The "
                    "folder structure has to be maintained.",
        options=arb_options)

    display = String(
        displayedName='Display',
        alias='DISPlay',
        options={'ON', 'OFF'},
        defaultValue='OFF',
        description="Turn Display on or off. OFF on start of device. "
                    "Control on hardware side can be reclaimed by pressing "
                    "the 'Local' key")
    display.readOnConnect = False
    display.writeOnConnect = True
    display.commandReadBack = True

    def display_setter(self, value):
        if value == 0 or value == '0' or value == "OFF":
            self.display = "OFF"
        else:
            self.display = "ON"

    display.__set__ = display_setter

    arbs = String(
        displayedName='Request Arbs',
        alias='MMEMory:CAT:DATA:ARB',
        defaultValue=r'INT:\BUILTIN',
        description="Request available arbitrary waveforms.",
        requiredAccessLevel=AccessLevel.EXPERT,
        accessMode=AccessMode.READONLY)
    arbs.commandFormat = '{alias}? {value}\n'
    arbs.commandReadBack = False
    arbs.readOnConnect = False

    def arbs_setter(self, value):
        self.arb_options = [a.strip('"') for a in value.split(",")
                            if ".arb" in a or ".seq" in a]

    arbs.__set__ = arbs_setter

    # overwriting connect so options can be set after reading values
    # from hardware
    async def connect(self):
        await wait_for(super().connect(), timeout=5)
        await self.getArbs()
