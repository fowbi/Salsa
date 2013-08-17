from setuptools import setup
import sys


version = '0.2'

setup(name='salsa',
      version=version,
      packages=['salsa'],
      description="",
      keywords='',
      author='',
      author_email='',
      license='',
      scripts=[
          'salsa/bin/salsa'
      ],
      install_requires=list(filter(None, [
          "pexpect",
          "pyyaml",
          "argparse" if sys.version_info[:2] < (2, 7) else None,
      ])),)
