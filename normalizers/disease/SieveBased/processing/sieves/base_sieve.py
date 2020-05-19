from typing import List, Optional, Dict, Set

from normalizers.disease.SieveBased.models.entities import SieveBasedDisease
from normalizers.disease.SieveBased.processing.sieves.sieve import Sieve
from normalizers.disease.SieveBased.processing.terminology import Terminology


class BaseSieve(Sieve):
    def __init__(self, terminology: Terminology, *, long_form_mode: bool = False):
        super(BaseSieve, self).__init__(terminology)
        self.long_form_mode = long_form_mode

    @property
    def name(self) -> str:
        return f'Base Sieve{" (expand_abbr)" if self.long_form_mode else ""}'

    @staticmethod
    def get_terminology_name_cui(name_to_cui_map: Dict[str, List[str]], name: str) -> Optional[str]:
        if name in name_to_cui_map and len(name_to_cui_map[name]) == 1:
            return name_to_cui_map[name][0]
        return None

    def exact_match_sieve(self, name: str) -> Optional[str]:
        # Check against already normalized names
        cui = self.get_terminology_name_cui(self.terminology.normalized_name_to_cui_map, name)
        if cui is not None:
            return cui
        # Check against terminology
        cui = self.get_terminology_name_cui(self.terminology.name_to_cui_map, name)
        return cui

    def normalize(self, names_knowledge_base: Set[str]) -> Optional[str]:
        for name in names_knowledge_base:
            cui = self.exact_match_sieve(name)
            if cui:
                return cui
        return None

    def apply(self, disease: SieveBasedDisease) -> Optional[str]:
        if self.long_form_mode:
            if disease.long_form:
                return self.exact_match_sieve(disease.long_form)
            else:
                return None
        else:
            return self.exact_match_sieve(disease.text)
