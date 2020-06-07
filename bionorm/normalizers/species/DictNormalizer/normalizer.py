from typing import Dict

from bionorm.common.models import Paper
from bionorm.common.util import process_file
from bionorm.normalizers.species.DictNormalizer.config import DictNormalizerConfig


class DictNormalizer:
    def __init__(self, config: DictNormalizerConfig):
        self.config = config
        self.names_dict: Dict[str, str] = {}

    @classmethod
    def default(cls) -> 'DictNormalizer':
        """Create normalizer with default config.

        Returns:
            Default DictNormalizer normalizer.
        """
        return DictNormalizer(DictNormalizerConfig())

    def load_data(self, *, verbose: bool = False):
        process_file(self.config.dict_path, self._load_names_dict, verbose=verbose, message='Loading species dict')

    def _load_names_dict(self, line: str):
        s_id, aliases = line.split('||')  # type: str, str
        for alias in aliases.split('|'):
            self.names_dict[alias.lower()] = s_id

    def normalize(self, paper: Paper):
        for passage in paper.passages:
            for mention in passage.species:
                text = mention.text.lower()
                if text in self.names_dict:
                    mention.id = self.names_dict[text][:-2]
