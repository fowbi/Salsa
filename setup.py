from setuptools import setup


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
          "docopt",
      ])),)
