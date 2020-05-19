from typing import Optional, Set, List

from common.SieveBased.models.entities import SieveBasedEntity
from common.SieveBased.processing.sieves import BaseSieve
from common.SieveBased.processing.terminology import Terminology


class HyphenationSieve(BaseSieve):
    """Hyphenation sieve.

    Looks for aliases where hyphens are replaced with spaces one-by-one and vice versa.
    """
    def __init__(self, terminology: Terminology):
        super(HyphenationSieve, self).__init__(terminology)

    @property
    def name(self) -> str:
        return "Hyphenation Sieve"

    def apply(self, entity: SieveBasedEntity) -> Optional[str]:
        self._transform_name(entity)
        return self.normalize(entity.names_knowledge_base)

    def _transform_name(self, entity: SieveBasedEntity):
        transformed_name: Set[str] = set()
        for name in entity.names_knowledge_base:
            transformed_name.update(self._hyphenate_string(name.split()))
            transformed_name.update(self._dehyphenate_string(name.split('-')))
        entity.names_knowledge_base.update(transformed_name)

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
