from os.path import join, dirname

from setuptools import setup, find_packages

setup(
    name='bionorm',
    version='0.0.7',
    packages=find_packages(),
    install_requires=['tqdm', 'nltk'],
    long_description=open(join(dirname(__file__), 'README.md')).read()
)
