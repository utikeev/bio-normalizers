import math
from datetime import datetime
from typing import Set, Dict, List, Callable, Tuple

from tqdm import tqdm

from normalizers.gene.GNormPlus.config import GNormPlusConfig
from normalizers.gene.GNormPlus.models.paper import Paper
from normalizers.gene.GNormPlus.processing.normalization import fill_gene_mention_hash, find_in_gene_tree, infer_multiple_genes, \
    process_abbreviations, rank_by_score_function, remove_gmt, append_gene_ids
from normalizers.gene.GNormPlus.processing.paper_processing import preprocess_paper
from normalizers.gene.GNormPlus.processing.species import assign_species
from normalizers.gene.GNormPlus.util.trees import PrefixTree


def _process_file(path: str, process_fn: Callable[[str], None], *, verbose: bool = False, message: str = ''):
    with open(path, 'r') as f:
        lines = f.readlines()
        if verbose:
            lines = tqdm(lines, message)
        for line in lines:
            if line.strip():
                process_fn(line)


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
    """

    def __init__(self, config: GNormPlusConfig):
        self.config = config
        self.gene_without_sp_prefix: Set[str] = set()
        self.suffix_translation_map: Dict[str, str] = {}
        self.prefix_map: Dict[str, str] = {}
        self.taxonomy_frequency: Dict[str, float] = {}
        self.human_viruses: Set[str] = set()
        self.filtering: Set[str] = set()
        self.gene_scoring: Dict[str, Tuple[str, int]] = {}
        self.gene_scoring_df: Dict[str, float] = {}

        self.chromosome_tree = PrefixTree(self.suffix_translation_map)
        self.gene_tree = PrefixTree(self.suffix_translation_map)
        self.family_name_tree = PrefixTree(self.suffix_translation_map)

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
        _process_tree(self.config.gene_tree_path, self.gene_tree, verbose=verbose,
                      message='Loading gene tree')
        _process_file(self.config.gene_scoring_path, self._process_gene_scoring, verbose=verbose,
                      message='Loading gene scorings')
        _process_file(self.config.gene_scoring_df_path, self._process_gene_scoring_df, verbose=verbose,
                      message='Loading gene scorings DF')

        _process_tree(self.config.chromosome_tree_path, self.chromosome_tree, verbose=verbose,
                      message='Loading chromosome tree')
        _process_tree(self.config.family_name_tree_path, self.family_name_tree, verbose=verbose,
                      message='Loading family name tree')

        _process_file(self.config.gene_without_sp_prefix_path, self._process_gene_without_sp_prefix, verbose=verbose,
                      message='Loading genes without special prefix')
        _process_file(self.config.suffix_translation_map_path, self._process_suffix_translation_map, verbose=verbose,
                      message='Loading suffix translation map')
        _process_file(self.config.prefix_id_map_path, self._process_prefix_map, verbose=verbose,
                      message='Loading prefix map')
        _process_file(self.config.taxonomy_freq_map_path, self._process_taxonomy_frequency, verbose=verbose,
                      message='Loading taxonomy frequency')
        _process_file(self.config.virus_human_list_path, self._process_virus_to_human, verbose=verbose,
                      message='Loading human virus list')
        _process_file(self.config.filtering_path, self._process_filtering, verbose=verbose,
                      message='Loading filtering')

        if verbose:
            print(f'Dictionaries loading took {datetime.now() - start_time}s')

    def _process_gene_without_sp_prefix(self, line: str):
        self.gene_without_sp_prefix.add(line)

    def _process_suffix_translation_map(self, line: str):
        parts: List[str] = line.split()
        self.suffix_translation_map[parts[0]] = parts[1]

    def _process_prefix_map(self, line: str):
        parts: List[str] = line.split('\t')
        self.prefix_map[parts[0]] = parts[1]

    def _process_taxonomy_frequency(self, line: str):
        parts: List[str] = line.split('\t')
        self.taxonomy_frequency[parts[0]] = float(parts[1]) / 200_000_000

    def _process_virus_to_human(self, line: str):
        self.human_viruses.add(line)

    def _process_filtering(self, line: str):
        self.filtering.add(line)

    def _process_gene_scoring(self, line: str):
        parts: List[str] = line.split('\t')
        self.gene_scoring[parts[0]] = (parts[1], int(parts[3]))

    def _process_gene_scoring_df(self, line: str):
        parts: List[str] = line.split('\t')
        if len(parts) == 1:
            self.gene_scoring_df_sum = float(line)
        else:
            count = float(parts[1])
            if count != .0:
                self.gene_scoring_df[parts[0]] = math.log10(self.gene_scoring_df_sum / count)

    def normalize(self, paper: Paper):
        gene_mention_hash: Dict[str, Dict[str, str]] = {}
        mention_hash: Set[str] = set()
        guaranteed_gene_to_id: Dict[str, str] = {}
        multi_gene_to_id: Dict[str, str] = {}

        preprocess_paper(paper, self.chromosome_tree)
        assign_species(paper, self.taxonomy_frequency, self.human_viruses, self.gene_without_sp_prefix, self.prefix_map)
        fill_gene_mention_hash(paper, gene_mention_hash, mention_hash, self.filtering)
        find_in_gene_tree(paper, guaranteed_gene_to_id, multi_gene_to_id, self.gene_tree, gene_mention_hash)
        infer_multiple_genes(guaranteed_gene_to_id, multi_gene_to_id, gene_mention_hash)
        process_abbreviations(paper, gene_mention_hash)
        rank_by_score_function(paper, gene_mention_hash, mention_hash, self.gene_scoring, self.gene_scoring_df)
        remove_gmt(paper, gene_mention_hash, self.gene_scoring)
        append_gene_ids(paper, gene_mention_hash, self.family_name_tree)
