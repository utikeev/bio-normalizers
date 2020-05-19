from typing import Optional, Set

from common.SieveBased.models.entities import SieveBasedEntity
from common.SieveBased.processing.sieves.base_sieve import BaseSieve
from common.SieveBased.processing.terminology import Terminology


class SymbolReplacementSieve(BaseSieve):
    """Symbol replacement sieve.

    Looks for aliases with replaced digits/words and bits of the common patterns changed to their analogues.
    """
    def __init__(self, terminology: Terminology):
        super(SymbolReplacementSieve, self).__init__(terminology)

    @property
    def name(self) -> str:
        return "Symbol Replacement Sieve"

    def apply(self, entity: SieveBasedEntity) -> Optional[str]:
        self._transform_name(entity)
        return self.normalize(entity.names_knowledge_base)

    def _transform_name(self, entity: SieveBasedEntity):
        transformed_names: Set[str] = set()
        for name in transformed_names:
            transformed_names.update(self._substitute_symbols_in_string_with_words(name))
            transformed_names.update(self._substitute_words_in_string_with_symbols(name))
        entity.names_knowledge_base.update(transformed_names)

    def _get_clinical_report_type_substitutions(self, name: str) -> Set[str]:
        new_strings: Set[str] = set()
        for digit, words in self.text_processor.digit_to_word_map.items():
            if digit not in name:
                continue
            for word in words:
                new_strings.add(name.replace(digit, word))
        return new_strings

    @staticmethod
    def _get_biomedical_type_substitutions(name: str) -> str:
        name = name.replace('and/or', 'and')
        name = name.replace('/', 'and')
        if ' (' in name and ')' in name:
            name = name.replace(' (', '').replace(')', '')
        if '(' in name and ')' in name:
            name = name.replace('(', '').replace(')', '')
        return name

    def _substitute_symbols_in_string_with_words(self, name: str) -> Set[str]:
        new_strings = self._get_clinical_report_type_substitutions(name)
        temp_strings: Set[str] = set()
        for new_string in new_strings:
            temp_strings.add(self._get_biomedical_type_substitutions(new_string))
        new_strings.update(temp_strings)
        new_strings.add(self._get_biomedical_type_substitutions(name))
        return new_strings

    def _substitute_words_in_string_with_symbols(self, name: str) -> Set[str]:
        new_strings: Set[str] = set()
        for word, digit in self.text_processor.word_to_digit_map.items():
            new_string = name.replace(word, digit)
            new_strings.add(new_string)
        return new_strings
