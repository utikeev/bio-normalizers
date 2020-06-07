from typing import List, Optional, Dict, Set

from bionorm.common.SieveBased.models import SieveBasedEntity
from bionorm.common.SieveBased.processing import Terminology
from bionorm.common.SieveBased.processing.sieves import Sieve


class BaseSieve(Sieve):
    """Base sieve.

    Basic sieve looking for the exact match. Also has long form mode, which looks for the full forms of abbreviations, instead of given
    name.
    """
    def __init__(self, terminology: Terminology, *, long_form_mode: bool = False):
        """
        Args:
            terminology (Terminology):
                Terminology to look for match into.
            long_form_mode (:obj:`bool`, defaults to :obj:`False`):
                Whether to check for long forms or original alias.
        """
        super(BaseSieve, self).__init__(terminology)
        self.long_form_mode = long_form_mode

    @property
    def name(self) -> str:
        return f'Base Sieve{" (expand_abbr)" if self.long_form_mode else ""}'

    @staticmethod
    def get_terminology_name_cui(name_to_cui_map: Dict[str, Set[str]], name: str) -> Optional[str]:
        """Find the exact match in ID map.

        Args:
            name_to_cui_map (Dict[str, List[str]]):
                Map from name to list of IDs.
            name (str):
                Name to normalize.

        Returns:
            ID if it is unique element for the name in the map. None, otherwise.
        """
        if name in name_to_cui_map and len(name_to_cui_map[name]) == 1:
            return next(iter(name_to_cui_map[name]))
        return None

    def exact_match_sieve(self, name: str) -> Optional[str]:
        """Find the exact match for name.

        First looks up in already normalized names map, which serves a function of cache.
        If not found, checks the terminology map.

        Args:
            name (str):
                Name to normalize.

        Returns:
            ID if the value was normalized. None, otherwise.
        """

        # Check against already normalized names
        cui = self.get_terminology_name_cui(self.terminology.normalized_name_to_cui_map, name)
        if cui is not None:
            return cui
        # Check against terminology
        cui = self.get_terminology_name_cui(self.terminology.name_to_cui_map, name)
        return cui

    def normalize(self, names_knowledge_base: Set[str]) -> Optional[str]:
        """Find the first exact match in the set of aliases.

        Args:
            names_knowledge_base (Set[str]):
                Aliases of name.

        Returns:
            ID if the value was normalized. None, otherwise.
        """
        for name in names_knowledge_base:
            cui = self.exact_match_sieve(name)
            if cui:
                return cui
        return None

    def apply(self, entity: SieveBasedEntity) -> Optional[str]:
        if self.long_form_mode:
            if entity.long_form:
                return self.exact_match_sieve(entity.long_form)
            else:
                return None
        else:
            return self.exact_match_sieve(entity.text)
