from typing import List, Tuple, Optional

from common.SieveBased.config.config import SieveBasedConfig
from common.SieveBased.models.entities import SieveBasedEntity, CUI_LESS
from common.SieveBased.processing.sieves import AffixationSieve, BaseSieve, EntityModifierSynonymsSieve, HyphenationSieve, \
    PartialMatchNCBISieve, PrepositionalTransformSieve, Sieve, SimpleNameSieve, StemmingSieve, SymbolReplacementSieve
from common.SieveBased.processing.terminology import Terminology
from common.SieveBased.util.text_processor import TextProcessor
from common.models.bio_entities import BioEntity


class SieveBasedNormalizer:
    """Sieve-based normalizer for entities.

    Notes:
        After creation of normalizer call load_data() to load all of the data.

    Attributes:
        config (SieveBasedConfig):
            Config for normalizer
    """
    def __init__(self, config: SieveBasedConfig):
        self.config = config
        self.text_processor = TextProcessor(config)
        self.terminology = Terminology(config.terminology_path, self.text_processor)
        self.sieves: List[Sieve] = [
            BaseSieve(self.terminology),
            BaseSieve(self.terminology, long_form_mode=True),
            PrepositionalTransformSieve(self.terminology),
            SymbolReplacementSieve(self.terminology),
            HyphenationSieve(self.terminology),
            AffixationSieve(self.terminology),
            EntityModifierSynonymsSieve(self.terminology),
            StemmingSieve(self.terminology),
            SimpleNameSieve(self.terminology),
            PartialMatchNCBISieve(self.terminology)
        ]

    def load_data(self, *, verbose: bool = False):
        """Loads the data used by normalizer.

        Args:
            verbose (:obj:`bool`, defaults to :obj:`False`):
                Whether to output verbose information about loading.
        """
        self.text_processor.load_data(verbose=verbose)
        self.terminology.load_data(verbose=verbose)

    def normalize_entities(self, entities_with_abb: List[Tuple[BioEntity, Optional[str]]], *, verbose: bool = False):
        """Normalize entities in paper in-place.

        Args:
            entities_with_abb (List[Tuple[BioEntity, Optional[str]]]):
                Entities to normalize with their abbreviations.
            verbose (:obj:`bool`, defaults to :obj:`False`):
                Whether to output verbose information about normalized entity.
        """
        for entity, long_form in entities_with_abb:
            sieve_entity = SieveBasedEntity(entity, self.text_processor, long_form)
            self._run_multi_pass_sieve(sieve_entity)
            if sieve_entity.id is None:
                sieve_entity.id = CUI_LESS
            if sieve_entity.normalizing_sieve_level != 1 or sieve_entity.id == CUI_LESS:
                self.terminology.store_normalized_entity(sieve_entity)
            if verbose:
                print(f'{sieve_entity.text}\t{sieve_entity.id}\t[{self.sieves[sieve_entity.normalizing_sieve_level].name}]')

    def _run_multi_pass_sieve(self, entity: SieveBasedEntity):
        for i, sieve in enumerate(self.sieves[:self.config.sieve_level]):
            entity.id = sieve.apply(entity)
            if entity.id is not None:
                entity.normalizing_sieve_level = i
                return
