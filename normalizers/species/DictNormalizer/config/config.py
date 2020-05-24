from os.path import join, dirname
from typing import NamedTuple

MODULE_PATH = join(dirname(__file__), '..')
DATA_PATH = join(MODULE_PATH, 'data')


class DictNormalizerConfig(NamedTuple):
    dict_path = join(DATA_PATH, 'species_dict.txt')
