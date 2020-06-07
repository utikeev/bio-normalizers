from os.path import join, dirname

from bionorm.common.models import Paper
from bionorm.common.SieveBased import SieveBasedNormalizer
from bionorm.common.SieveBased.config import SieveBasedConfig

DATA_PATH = join(dirname(__file__), 'data')


class ChemicalsSieveBasedNormalizer(SieveBasedNormalizer):
    def __init__(self, config: SieveBasedConfig):
        super(ChemicalsSieveBasedNormalizer, self).__init__(config)

    @classmethod
    def default(cls) -> 'ChemicalsSieveBasedNormalizer':
        """Create normalizer with default config.

        Returns:
            Default sieve-based normalizer.
        """
        return ChemicalsSieveBasedNormalizer(SieveBasedConfig(terminology_path=join(DATA_PATH, 'mesh_terminology.txt')))

    def normalize(self, paper: Paper, *, verbose: bool = False):
        all_chemicals = [(chemical, paper.abb_sf_to_lf.get(chemical)) for passage in paper.passages for chemical in passage.chemicals]
        self.normalize_entities(all_chemicals, verbose=verbose)
