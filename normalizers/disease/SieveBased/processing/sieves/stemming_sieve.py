from typing import Optional, Set

from normalizers.disease.SieveBased.models.entities import SieveBasedDisease
from normalizers.disease.SieveBased.processing.sieves.base_sieve import BaseSieve
from normalizers.disease.SieveBased.processing.terminology import Terminology


class StemmingSieve(BaseSieve):
    def __init__(self, terminology: Terminology):
        super(StemmingSieve, self).__init__(terminology)

    def apply(self, disease: SieveBasedDisease) -> Optional[str]:
        self._transform_name(disease)
        return self.normalize(disease.stemmed_names_knowledge_base)

    def _transform_name(self, disease: SieveBasedDisease):
        transformed_name: Set[str] = set()
        for name in disease.names_knowledge_base:
            transformed_name.add(self.text_processor.get_stemmed_phrase(name))
        disease.stemmed_names_knowledge_base.update(transformed_name)

    def exact_match_sieve(self, name: str) -> Optional[str]:
        # Check against already normalized names
        cui = self.get_terminology_name_cui(self.terminology.stemmed_normalized_name_to_cui_map, name)
        if cui is not None:
            return cui
        # Check against terminology
        cui = self.get_terminology_name_cui(self.terminology.stemmed_name_to_cui_map, name)
        return cui
