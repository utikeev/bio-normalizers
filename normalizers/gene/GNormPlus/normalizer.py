from datetime import datetime
from typing import Set, Dict, List, Callable

from tqdm import tqdm

from normalizers.gene.GNormPlus.config import GNormPlusConfig
from normalizers.gene.GNormPlus.util.trees import PrefixTree


def _process_file(path: str, process_fn: Callable[[str], None], *, verbose: bool = False, message: str = ''):
    with open(path, 'r') as f:
        lines = f.readlines()
        if verbose:
            lines = tqdm(lines, message)
        for line in lines:
            stripped = line.strip()
            if stripped != '':
                process_fn(stripped)


def _process_tree(path: str, tree: PrefixTree, *, verbose: bool = False, message: str = ''):
    with open(path, 'r') as f:
        lines = f.readlines()
        if verbose:
            lines = tqdm(lines, message)
        tree.load_from_lines(lines)


class GNormPlus:
    """GNormPlus normalizer.

    Notes:
        After creation of normalizer call load_data() to load all of the data.

    Attributes:
        config (GNormPlusConfig):
            Config for normalizer.
        gene_without_sp_prefix (Set[str]):
            TODO
        suffix_translation_map (Dict[str, str]):
            TODO
        genus_map (Dict[str, str]):
            TODO
        taxon_to_genus (Set[str]):
            TODO
        prefix_map (Dict[str, str]):
            TODO
        taxonomy_frequency (Dict[str, float]):
            TODO
        human_viruses (Set[str]):
            TODO
        gene_map (Dict[str, str]):
            TODO
        gene_to_protein (Dict[str, str]):
            TODO
        gene_to_homoid (Dict[str, str]):
            TODO
    """

    def __init__(self, config: GNormPlusConfig):
        self.config = config
        self.gene_without_sp_prefix: Set[str] = set()
        self.suffix_translation_map: Dict[str, str] = dict()
        self.genus_map: Dict[str, str] = dict()
        self.taxon_to_genus: Set[str] = set()
        self.prefix_map: Dict[str, str] = dict()
        self.taxonomy_frequency: Dict[str, float] = dict()
        self.human_viruses: Set[str] = set()
        self.gene_map: Dict[str, str] = dict()
        self.gene_to_protein: Dict[str, str] = dict()
        self.gene_to_homoid: Dict[str, str] = dict()

        self.species_tree = PrefixTree(self.suffix_translation_map)
        self.cell_tree = PrefixTree(self.suffix_translation_map)

    @classmethod
    def default(cls) -> 'GNormPlus':
        """Create normalizer with default config.

        Returns:
            Default GNormPlus normalizer.
        """
        return GNormPlus(GNormPlusConfig())

    def load_data(self, *, verbose: bool = False) -> None:
        """Loads the data used by normalizer.

        Args:
            verbose (:obj:`bool`, defaults to :obj:`False`):
                Whether to output verbose information about loading.
        """
        start_time = datetime.now()

        if verbose:
            print(f'Loading dictionaries…')

        _process_file(self.config.gene_without_sp_prefix_path, self._process_gene_without_sp_prefix, verbose=verbose,
                      message='Loading genes without special prefix')
        _process_file(self.config.suffix_translation_map_path, self._process_suffix_translation_map, verbose=verbose,
                      message='Loading suffix translation map')
        # _process_tree(self.config.species_tree_path, self.species_tree, verbose=verbose,
        #               message='Loading species tree')
        _process_tree(self.config.cell_tree_path, self.cell_tree, verbose=verbose,
                      message='Loading cell tree')
        _process_file(self.config.genus_id_map_path, self._process_genus_map, verbose=verbose,
                      message='Loading genus map')
        _process_file(self.config.taxonomy_id_for_genus_path, self._process_taxon_id_for_genus, verbose=verbose,
                      message='Loading taxonomy id')
        _process_file(self.config.prefix_id_map_path, self._process_prefix_map, verbose=verbose,
                      message='Loading prefix map')
        _process_file(self.config.taxonomy_freq_map_path, self._process_taxonomy_frequency, verbose=verbose,
                      message='Loading taxonomy frequency')
        _process_file(self.config.virus_human_list_path, self._process_virus_to_human, verbose=verbose,
                      message='Loading human virus list')
        _process_file(self.config.gene_id_map_path, self._process_gene_id, verbose=verbose,
                      message='Loading gene IDs')
        _process_file(self.config.gene_to_protein_map_path, self._process_normalization_to_protein, verbose=verbose,
                      message='Loading gene to protein map')
        _process_file(self.config.gene_to_homoid_map_path, self._process_homologene, verbose=verbose,
                      message='Loading gene to homoid map')

        if verbose:
            print(f'Dictionaries loading took {datetime.now() - start_time}s')

    def _process_gene_without_sp_prefix(self, line: str):
        self.gene_without_sp_prefix.add(line)

    def _process_suffix_translation_map(self, line: str):
        parts: List[str] = line.split()
        self.suffix_translation_map[parts[0]] = parts[1]

    def _process_genus_map(self, line: str):
        parts: List[str] = line.split('\t')
        self.genus_map[parts[0]] = parts[1]

    def _process_taxon_id_for_genus(self, line: str):
        self.taxon_to_genus.add(line)

    def _process_prefix_map(self, line: str):
        parts: List[str] = line.split('\t')
        self.prefix_map[parts[0]] = parts[1]

    def _process_taxonomy_frequency(self, line: str):
        parts: List[str] = line.split('\t')
        self.taxonomy_frequency[parts[0]] = float(parts[1]) / 200_000_000

    def _process_virus_to_human(self, line: str):
        self.human_viruses.add(line)

    def _process_gene_id(self, line: str):
        parts: List[str] = line.split('\t')
        self.gene_map[parts[0]] = parts[1]

    def _process_normalization_to_protein(self, line: str):
        parts: List[str] = line.split('\t')
        self.gene_to_protein[parts[0]] = parts[1]

    def _process_homologene(self, line: str):
        parts: List[str] = line.split('\t')
        self.gene_to_homoid[parts[0]] = parts[1]
