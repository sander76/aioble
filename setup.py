from distutils.core import setup
from setuptools import find_packages

setup(name='aioble',
      version='0.0.1',
      description='An asynchronous (asyncio) bluetooth low energy (BLE) python library',
      author='detect labs',
      author_email='code@detectlabs.io',
      url='https://github.com/detectlabs/aioble',
      packages=find_packages(exclude=('examples')),
      package_data={
          'aioble.dotnet': ['*.dll', ]
      },
      )
