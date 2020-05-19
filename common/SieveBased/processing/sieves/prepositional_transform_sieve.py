from typing import Optional, List, Set

from common.SieveBased.models.entities import SieveBasedEntity
from common.SieveBased.processing.sieves.base_sieve import BaseSieve
from common.SieveBased.processing.terminology import Terminology


class PrepositionalTransformSieve(BaseSieve):
    """Prepositional Transform sieve.

    Looks for aliases with some of the manipulations with prepositions.

    If the phrase has preposition:
    1. Create new phrase by substituting it with other prepositions
    2. Remove the preposition in the phrase and swap the surrounding parts of the string

    If the phrase doesn't have prepositions, generate some:
    1. By inserting one near the beginning
    2. By inserting one near the end
    """
    def __init__(self, terminology: Terminology):
        super(PrepositionalTransformSieve, self).__init__(terminology)

    @property
    def name(self) -> str:
        return "Prepositional Transform Sieve"

    def apply(self, entity: SieveBasedEntity) -> Optional[str]:
        self._init(entity)
        self._transform_name(entity)
        return self.normalize(entity.names_knowledge_base)

    @staticmethod
    def _init(entity: SieveBasedEntity):
        entity.names_knowledge_base.add(entity.text)
        if entity.long_form:
            entity.names_knowledge_base.add(entity.long_form)

    def _transform_name(self, entity: SieveBasedEntity):
        transformed_names: Set[str] = set()
        for name in entity.names_knowledge_base:
            preposition_in_name = self.text_processor.get_preposition(name)
            if preposition_in_name:
                transformed_names.update(self._substitute_prepositions_in_phrase(preposition_in_name, name))
                transformed_names.add(self._swap_phrasal_subject_and_object(preposition_in_name, name.split()))
            else:
                transformed_names.update(self._insert_prepositions_in_phrase(name.split()))
        entity.names_knowledge_base.update(transformed_names)

    def _insert_prepositions_in_phrase(self, tokens: List[str]) -> Set[str]:
        new_prepositional_phrases: Set[str] = set()
        for preposition in self.text_processor.prepositions:
            new_phrase = f'{self.text_processor.get_token_substring(tokens, 1, len(tokens))} {preposition} {tokens[0]}'
            new_prepositional_phrases.add(new_phrase)
            new_phrase = f'{tokens[-1]} {preposition} {self.text_processor.get_token_substring(tokens, 0, len(tokens) - 1)}'
            new_prepositional_phrases.add(new_phrase)
        return new_prepositional_phrases

    def _substitute_prepositions_in_phrase(self, preposition_in_name: str, name: str) -> Set[str]:
        new_prepositional_phrases: Set[str] = set()
        for preposition in self.text_processor.prepositions:
            if preposition_in_name == preposition:
                continue
            new_prepositional_phrases.add(name.replace(f' {preposition_in_name} ', f' {preposition} '))
        return new_prepositional_phrases

    def _swap_phrasal_subject_and_object(self, preposition_in_name: str, tokens: List[str]) -> str:
        preposition_index = self.text_processor.get_token_index(tokens, preposition_in_name)
        if preposition_index is None:
            sentence = ' '.join(tokens)
            raise ValueError(f'Preposition {preposition_in_name} isn\'t located in sentence. Sentence:\n\t{sentence}')
        obj = self.text_processor.get_token_substring(tokens, preposition_index + 1, len(tokens))
        subj = self.text_processor.get_token_substring(tokens, 0, preposition_index)
        return f'{obj} {subj}'
