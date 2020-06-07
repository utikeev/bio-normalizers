from os.path import join, dirname

from setuptools import setup, find_packages

setup(
    name='bionorm',
    version='0.0.8',
    packages=find_packages(),
    install_requires=['tqdm', 'nltk'],
    include_package_data=True,
    package_data={
        'bionorm': ['bionorm/common/SieveBased/data/*.txt'],
    },
    long_description=open(join(dirname(__file__), 'README.md')).read()
)
