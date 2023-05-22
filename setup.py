#!/usr/bin/env python
from os.path import dirname, join, realpath

from karabo.packaging.versioning import device_scm_version
from setuptools import find_packages, setup

ROOT_FOLDER = dirname(realpath(__file__))
scm_version = device_scm_version(
    ROOT_FOLDER,
    join(ROOT_FOLDER, 'src', 'FunctionGenerator', '_version.py')
)


setup(name='FunctionGenerator',
      use_scm_version=scm_version,
      author='amunnich',
      author_email='amunnich',
      description='',
      long_description='',
      url='',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      entry_points={
          'karabo.middlelayer_device': [
              'AFG31000 = FunctionGenerator.AFG31000:AFG31000',
              'Keysight33512 = FunctionGenerator.Keysight33512:Keysight33512',
              'Keysight33511 = FunctionGenerator.Keysight33511:Keysight33511'
          ],
      },
      package_data={},
      requires=[],
      )
