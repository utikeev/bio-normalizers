from os.path import join, dirname

from setuptools import setup, find_packages

prefixed_packages = {'bionorm.{}'.format(p): p.replace('.', '/') for p in find_packages()}

setup(
    name='bionorm',
    version='0.0.1',
    packages=prefixed_packages.keys(),
    package_dir=prefixed_packages,
    long_description=open(join(dirname(__file__), 'README.md')).read()
)
