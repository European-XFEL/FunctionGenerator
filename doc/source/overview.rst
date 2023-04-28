********
Overview
********

The aim of this package is to provide a common base for all
function generators that follow the same SCPI syntax.
The specific implementation of vendors
and models can then be built on top of that base.

Currently implemented are the following vendors and models:

1. **Tektronix**:

    - AFG31252

2. **Keysight**:

    - 33511
    - 33512

    Keysight models of the 33500 and 33600 Series have the same
    SCPI reference. Models may very however in frequency range and
    availability of features, as well as in number of channels:

    ==================== ======== ======== ======== ======== ======== ======== ========= =========
    Bandwidth             20 MHz   20 MHz   30 MHz   30 MHz   80 MHz   80 MHz   120 MHz   120 MHz
    ==================== ======== ======== ======== ======== ======== ======== ========= =========
    Number of channels     1        2        1        2        1        2        1        2
    Waveform generator    33509B   33510B   33519B   33520B    x        x        x        x
    with arbitr. cap.     33511B   33512B   33521B   33522B   33611A   33612A   33621A    33622A
    ==================== ======== ======== ======== ======== ======== ======== ========= =========



