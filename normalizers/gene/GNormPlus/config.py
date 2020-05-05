from os.path import dirname, join
from typing import NamedTuple

MODULE_PATH = dirname(__file__)
DATA_PATH = join(MODULE_PATH, 'data')
TREES_PATH = join(DATA_PATH, 'trees')


class GNormPlusConfig(NamedTuple):
    """Configuration class which holds options and paths to data files.

    Is used for creation of :class:`normalizers.gene.GNormPlus.normalizer.GNormPlus` normalizer.

    Args:
        focus_species (:obj:`str`, optional, defaults to 'all'):
            ID of species
        gene_id_match (:obj:`bool`, optional, defaults to :obj:`True`):
            Whether to match genes to their IDs
        normalization_to_protein (:obj:`bool`, optional, defaults to :obj:`False`):
            TODO
        homologene_id  (:obj:`bool`, optional, defaults to :obj:`False`):
            TODO
        show_unnormalized_mention  (:obj:`bool`, optional, defaults to :obj:`False`):
            TODO
        gene_without_sp_prefix_path (:obj:`str`, optional):
            TODO
        suffix_translation_map_path (:obj:`str`, optional):
            TODO
        genus_id_map_path (:obj:`str`, optional):
            TODO
        taxonomy_id_for_genus_path (:obj:`str`, optional):
            TODO
        prefix_id_map_path (:obj:`str`, optional):
            TODO
        taxonomy_freq_map_path (:obj:`str`, optional):
            TODO
        virus_human_list_path (:obj:`str`, optional):
            TODO
        gene_id_map_path (:obj:`str`, optional):
            TODO
        gene_to_protein_map_path (:obj:`str`, optional):
            TODO
        gene_to_homoid_map_path (:obj:`str`, optional):
            TODO
        species_tree_path (:obj:`str`, optional):
            TODO
        cell_tree_path (:obj:`str`, optional):
            TODO
    """
    focus_species: str = 'all'
    gene_id_match: bool = True
    normalization_to_protein: bool = False
    homologene_id: bool = False
    show_unnormalized_mention: bool = False

    gene_without_sp_prefix_path: str = join(DATA_PATH, 'GeneWithoutSPPrefix.txt')
    suffix_translation_map_path: str = join(DATA_PATH, 'SuffixTranslationMap.txt')
    genus_id_map_path: str = join(DATA_PATH, 'SPGenus.txt')
    taxonomy_id_for_genus_path: str = join(DATA_PATH, 'TaxonomyForGenus.txt')
    prefix_id_map_path: str = join(DATA_PATH, 'SPPrefix.txt')
    taxonomy_freq_map_path: str = join(DATA_PATH, 'TaxonomyFrequency.txt')
    virus_human_list_path: str = join(DATA_PATH, 'SP_Virus2HumanList.txt')

    gene_id_map_path: str = join(DATA_PATH, 'GeneIDs.txt')
    gene_to_protein_map_path: str = join(DATA_PATH, 'Gene2Protein.txt')
    gene_to_homoid_map_path: str = join(DATA_PATH, 'Gene2Homoid.txt')

    species_tree_path: str = join(TREES_PATH, 'PT_NewSpecies.txt')
    cell_tree_path: str = join(TREES_PATH, 'PT_Cell.txt')
