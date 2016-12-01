import versioneer
from setuptools import setup

setup(name='remotekernel',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      author='Brookhaven National Laboratory',
      packages=['remotekernel'],
      description='A custom KernelManager for launching remote IPython kernels',
      url='http://github.com/danielballan/remotekernel',
      platforms='Cross platform (Linux, Mac OSX, Windows)',
      )
