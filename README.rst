***********************************
FunctionGenerator Device (MiddleLayer)
***********************************

This package contains Karabo device classes for Keysight function generators.

Dependencies
============

This Karabo device depends on another Karabo device: scpiML version 1.0.9-2.14.1.

Testing
=======

Every Karabo device in Python is shipped as a regular python package.
In order to make the device visible to any device-server you have to install
the package to Karabo's own Python environment.

Simply type:

``pip install -e .``

in the directory of where the ``setup.py`` file is located, or use the ``karabo``
utility script:

``karabo develop FunctionGenerator``

Running
=======

If you want to manually start a server using this device, simply type:

``karabo-middlelayerserver serverId=middleLayerServer/1 deviceClasses=FunctionGenerator``

Or just use (a properly configured):

``karabo-start``

Disclaimer
==========

This software is released by the European XFEL GmbH as is and without any warranty under the GPLv3 license. If you have questions on contributing to the project, please get in touch at opensource@xfel.eu.
