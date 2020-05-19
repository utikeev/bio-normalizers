from typing import List

from common.models.paper import Paper
from normalizers.disease.SieveBased.config.config import SieveBasedConfig
from normalizers.disease.SieveBased.models.entities import SieveBasedDisease, CUI_LESS
from normalizers.disease.SieveBased.processing.sieves import AffixationSieve, BaseSieve, DiseaseModifierSynonymsSieve, HyphenationSieve, \
    PartialMatchNCBISieve, PrepositionalTransformSieve, Sieve, SimpleNameSieve, StemmingSieve, SymbolReplacementSieve
from normalizers.disease.SieveBased.processing.terminology import Terminology
from normalizers.disease.SieveBased.util.text_processor import TextProcessor


class SieveBasedNormalizer:
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
            DiseaseModifierSynonymsSieve(self.terminology),
            StemmingSieve(self.terminology),
            SimpleNameSieve(self.terminology),
            PartialMatchNCBISieve(self.terminology)
        ]

    @classmethod
    def default(cls) -> 'SieveBasedNormalizer':
        """Create normalizer with default config.

        Returns:
            Default sieve-based normalizer.
        """
        return SieveBasedNormalizer(SieveBasedConfig())

    def load(self, *, verbose: bool = False):
        self.text_processor.load_data(verbose=verbose)
        self.terminology.load(verbose=verbose)

    def normalize(self, paper: Paper, *, verbose: bool = False):
        all_diseases: List[SieveBasedDisease] = []
        for passage in paper.passages:
            for disease in passage.diseases:
                long_form = paper.abb_sf_to_lf[disease] if disease in paper.abb_sf_to_lf else None
                sieve_disease = SieveBasedDisease(disease, self.text_processor, long_form)
                all_diseases.append(sieve_disease)
                self._run_multi_pass_sieve(sieve_disease)
                if sieve_disease.id is None:
                    sieve_disease.id = CUI_LESS
                if sieve_disease.normalizing_sieve_level != 1 or sieve_disease.id == CUI_LESS:
                    self.terminology.store_normalized_disease(sieve_disease)
                if verbose:
                    print(f'{sieve_disease.text}\t{sieve_disease.id}\t[{self.sieves[sieve_disease.normalizing_sieve_level].name}]')

    def _run_multi_pass_sieve(self, disease: SieveBasedDisease):
        for i, sieve in enumerate(self.sieves[:self.config.sieve_level]):
            disease.id = sieve.apply(disease)
            if disease.id is not None:
                disease.normalizing_sieve_level = i
                return
