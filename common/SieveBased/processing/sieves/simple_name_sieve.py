from typing import Optional, Set, List

from common.SieveBased.models.entities import SieveBasedEntity
from common.SieveBased.processing.sieves import BaseSieve
from common.SieveBased.processing.terminology import Terminology


class SimpleNameSieve(BaseSieve):
    """Simple Name sieve.

    Looks for shorter aliases by removing the word before last and the first word.
    """
    def __init__(self, terminology: Terminology):
        super(SimpleNameSieve, self).__init__(terminology)

    @property
    def name(self) -> str:
        return "Simple Name Sieve"

    def apply(self, entity: SieveBasedEntity) -> Optional[str]:
        names_for_transformation = self._get_names_for_transformation(entity)
        names_knowledge_base = self._transform_name(names_for_transformation)
        cui = self.normalize(names_knowledge_base)
        return cui if cui is not None else self.get_terminology_name_cui(self.terminology.simple_name_to_cui_map, entity.text)

    @staticmethod
    def _get_names_for_transformation(entity: SieveBasedEntity) -> Set[str]:
        names_for_transformation: Set[str] = set()
        names_for_transformation.add(entity.text)
        if entity.long_form:
            names_for_transformation.add(entity.long_form)
        return names_for_transformation

    def _transform_name(self, names_for_transformation: Set[str]) -> Set[str]:
        transformed_names: Set[str] = set()
        for name in names_for_transformation:
            transformed_names.update(self._delete_phrasal_modifier(name.split()))
        return transformed_names

    def _delete_phrasal_modifier(self, tokens: List[str]) -> Set[str]:
        new_phrases: Set[str] = set()
        if len(tokens) > 3:
            new_phrase = self.text_processor.get_token_substring(tokens, 0, len(tokens) - 2) + ' ' + tokens[len(tokens) - 1]
            new_phrases.add(new_phrase)
            new_phrase = self.text_processor.get_token_substring(tokens, 1, len(tokens))
            new_phrases.add(new_phrase)
        return new_phrases
