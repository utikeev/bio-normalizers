from typing import Optional, Set

from bionorm.common.SieveBased.models import SieveBasedEntity
from bionorm.common.SieveBased.processing import Terminology
from bionorm.common.SieveBased.processing.sieves.base_sieve import BaseSieve


class StemmingSieve(BaseSieve):
    """Stemming sieve.

    Looks for stemmed alias.
    """
    def __init__(self, terminology: Terminology):
        super(StemmingSieve, self).__init__(terminology)

    @property
    def name(self) -> str:
        return "Stemming Sieve"

    def apply(self, entity: SieveBasedEntity) -> Optional[str]:
        self._transform_name(entity)
        return self.normalize(entity.stemmed_names_knowledge_base)

    def _transform_name(self, entity: SieveBasedEntity):
        transformed_name: Set[str] = set()
        for name in entity.names_knowledge_base:
            transformed_name.add(self.text_processor.get_stemmed_phrase(name))
        entity.stemmed_names_knowledge_base.update(transformed_name)

    def exact_match_sieve(self, name: str) -> Optional[str]:
        cui = self.get_terminology_name_cui(self.terminology.stemmed_normalized_name_to_cui_map, name)
        if cui is not None:
            return cui
        cui = self.get_terminology_name_cui(self.terminology.stemmed_name_to_cui_map, name)
        return cui
