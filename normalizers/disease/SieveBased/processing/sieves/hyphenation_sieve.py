from typing import Optional, Set, List

from normalizers.disease.SieveBased.models.entities import SieveBasedDisease
from normalizers.disease.SieveBased.processing.sieves.base_sieve import BaseSieve
from normalizers.disease.SieveBased.processing.terminology import Terminology


class HyphenationSieve(BaseSieve):
    def __init__(self, terminology: Terminology):
        super(HyphenationSieve, self).__init__(terminology)

    def apply(self, disease: SieveBasedDisease) -> Optional[str]:
        self._transform_name(disease)
        return self.normalize(disease.names_knowledge_base)

    def _transform_name(self, disease: SieveBasedDisease):
        transformed_name: Set[str] = set()
        for name in disease.names_knowledge_base:
            transformed_name.update(self._hyphenate_string(name.split()))
            transformed_name.update(self._dehyphenate_string(name.split('-')))
        disease.names_knowledge_base.update(transformed_name)

    @staticmethod
    def _hyphenate_string(tokens: List[str]) -> Set[str]:
        hyphenated_strings: Set[str] = set()
        for i in range(1, len(tokens)):
            hyphenated_strings.add(' '.join(tokens[:i]) + '-' + ' '.join(tokens[i:]))
        return hyphenated_strings

    @staticmethod
    def _dehyphenate_string(tokens: List[str]) -> Set[str]:
        dehyphenated_strings: Set[str] = set()
        for i in range(1, len(tokens)):
            dehyphenated_strings.add('-'.join(tokens[:i]) + ' ' + '-'.join(tokens[i:]))
        return dehyphenated_strings
