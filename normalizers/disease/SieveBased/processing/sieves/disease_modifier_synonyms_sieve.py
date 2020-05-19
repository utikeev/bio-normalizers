from typing import Optional, Set, List

from normalizers.disease.SieveBased.models.entities import SieveBasedDisease
from normalizers.disease.SieveBased.processing.sieves.base_sieve import BaseSieve
from normalizers.disease.SieveBased.processing.terminology import Terminology


class DiseaseModifierSynonymsSieve(BaseSieve):
    def __init__(self, terminology: Terminology):
        super(DiseaseModifierSynonymsSieve, self).__init__(terminology)

    def apply(self, disease: SieveBasedDisease) -> Optional[str]:
        if disease.text not in self.text_processor.plural_synonyms and disease.text not in self.text_processor.singular_synonyms:
            self._transform_name(disease)
            return self.normalize(disease.names_knowledge_base)
        return None

    def _transform_name(self, disease: SieveBasedDisease):
        transformed_names: Set[str] = set()
        for name in disease.names_knowledge_base:
            tokens = name.split()
            modifier = self._get_modifier(tokens, self.text_processor.plural_synonyms)
            if modifier:
                transformed_names.update(
                    self._substitute_disease_modifier_with_synonyms(name, modifier, self.text_processor.plural_synonyms)
                )
                transformed_names.add(self._delete_tail_modifier(tokens, modifier))
                continue

            modifier = self._get_modifier(tokens, self.text_processor.singular_synonyms)
            if modifier:
                transformed_names.update(
                    self._substitute_disease_modifier_with_synonyms(name, modifier, self.text_processor.singular_synonyms)
                )
                transformed_names.add(self._delete_tail_modifier(tokens, modifier))
                continue
            transformed_names.update(self._append_modifier(name, self.text_processor.singular_synonyms))

        disease.names_knowledge_base.update(transformed_names)

    @staticmethod
    def _append_modifier(string: str, modifiers: List[str]) -> Set[str]:
        new_phrases: Set[str] = set()
        for modifier in modifiers:
            new_phrases.add(f'{string} {modifier}')
        return new_phrases

    def _delete_tail_modifier(self, tokens: List[str], modifier: str) -> Optional[str]:
        return self.text_processor.get_token_substring(tokens, 0, len(tokens) - 1) if tokens[-1] == modifier else None

    @staticmethod
    def _substitute_disease_modifier_with_synonyms(string: str, to_replace_word: str, synonyms: List[str]) -> Set[str]:
        new_phrases: Set[str] = set()
        for synonym in synonyms:
            if to_replace_word == synonym:
                continue
            new_phrases.add(string.replace(to_replace_word, synonym))
        return new_phrases

    def _get_modifier(self, tokens: List[str], modifiers: List[str]) -> Optional[str]:
        for modifier in modifiers:
            index = self.text_processor.get_token_index(tokens, modifier)
            if index:
                return tokens[index]
        return None
