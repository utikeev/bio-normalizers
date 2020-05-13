from os.path import dirname, join
from typing import NamedTuple

MODULE_PATH = dirname(__file__)
DATA_PATH = join(MODULE_PATH, 'data')
TREES_PATH = join(DATA_PATH, 'trees')


class GNormPlusConfig(NamedTuple):
    """Configuration class which holds options and paths to data files.

    Is used for creation of :class:`normalizers.gene.GNormPlus.normalizer.GNormPlus` normalizer.

    Args:
    """
    gene_without_sp_prefix_path: str = join(DATA_PATH, 'GeneWithoutSPPrefix.txt')
    suffix_translation_map_path: str = join(DATA_PATH, 'SuffixTranslationMap.txt')
    prefix_id_map_path: str = join(DATA_PATH, 'SPPrefix.txt')
    taxonomy_freq_map_path: str = join(DATA_PATH, 'TaxonomyFrequency.txt')
    virus_human_list_path: str = join(DATA_PATH, 'SP_Virus2HumanList.txt')
    filtering_path: str = join(DATA_PATH, 'Filtering.txt')
    gene_scoring_path: str = join(DATA_PATH, 'GeneScoring.txt')
    gene_scoring_df_path: str = join(DATA_PATH, 'GeneScoring.DF.txt')

    chromosome_tree_path: str = join(TREES_PATH, 'PT_GeneChromosome.txt')
    gene_tree_path: str = join(TREES_PATH, 'PT_Gene.txt')
    family_name_tree_path: str = join(TREES_PATH, 'PT_FamilyName.txt')


TEST_CONFIG = GNormPlusConfig(
    gene_tree_path=join(TREES_PATH, 'PT_GeneTest.txt'),
    gene_scoring_path=join(DATA_PATH, 'GeneScoringTest.txt'),
    gene_scoring_df_path=join(DATA_PATH, 'GeneScoring.DFTest.txt')
)
