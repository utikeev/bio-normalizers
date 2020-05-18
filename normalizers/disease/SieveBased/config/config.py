from os.path import dirname, join
from typing import NamedTuple, Type

from nltk import PorterStemmer, StemmerI

ROOT_PATH = join(dirname(__file__), '..')
DATA_PATH = join(ROOT_PATH, 'data')


class SieveBasedConfig(NamedTuple):
    """Configuration class which holds options and paths to data files.

    Is used for creation of :class:`normalizers.disease.SieveBased.normalizer.SieveBased` normalizer.

    Args:
    """
    use_nltk_stopwords: bool = False
    stopwords_path: str = join(DATA_PATH, 'stopwords.txt')
    stemmer_constructor: Type[StemmerI] = PorterStemmer
    spell_check_map_path: str = join(DATA_PATH, 'ncbi-spell-check.txt')
    prepositions_path: str = join(DATA_PATH, 'prepositions.txt')
    digit_map_path: str = join(DATA_PATH, 'number.txt')
    suffix_map_path: str = join(DATA_PATH, 'suffix.txt')
    prefix_map_path: str = join(DATA_PATH, 'prefix.txt')
    affix_map_path: str = join(DATA_PATH, 'affix.txt')
    singular_synonyms_path: str = join(DATA_PATH, 'singular_synonyms.txt')
    plural_synonyms_path: str = join(DATA_PATH, 'plural_synonyms.txt')

#
# TEST_CONFIG = SieveBasedConfig(
#     gene_tree_path=join(TREES_PATH, 'PT_GeneTest.txt'),
#     gene_scoring_path=join(DATA_PATH, 'GeneScoringTest.txt'),
#     gene_scoring_df_path=join(DATA_PATH, 'GeneScoring.DFTest.txt')
# )
