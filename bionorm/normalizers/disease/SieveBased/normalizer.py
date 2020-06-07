from os.path import join, dirname

from bionorm.common.models import Paper
from bionorm.common.SieveBased import SieveBasedNormalizer
from bionorm.common.SieveBased.config import SieveBasedConfig

DATA_PATH = join(dirname(__file__), 'data')


class DiseaseSieveBasedNormalizer(SieveBasedNormalizer):
    def __init__(self, config: SieveBasedConfig):
        super(DiseaseSieveBasedNormalizer, self).__init__(config)

    @classmethod
    def default(cls) -> 'DiseaseSieveBasedNormalizer':
        """Create normalizer with default config.

        Returns:
            Default sieve-based normalizer.
        """
        return DiseaseSieveBasedNormalizer(SieveBasedConfig(terminology_path=join(DATA_PATH, 'mesh_terminology.txt')))

    def normalize(self, paper: Paper, *, verbose: bool = False):
        all_diseases = [(disease, paper.abb_sf_to_lf.get(disease.text.lower())) for passage in paper.passages for disease in passage.diseases]
        self.normalize_entities(all_diseases, verbose=verbose)
