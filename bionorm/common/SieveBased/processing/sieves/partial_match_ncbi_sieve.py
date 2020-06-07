from typing import Optional, Set, List, Dict

from bionorm.common.SieveBased.models import SieveBasedEntity
from bionorm.common.SieveBased.processing import Terminology
from bionorm.common.SieveBased.processing.sieves.base_sieve import BaseSieve


class PartialMatchNCBISieve(BaseSieve):
    """Partial Match sieve.

    Looks for the best candidate in terminology which has minimal length and maximum of the common words with alias
    (shortest and most similar entity).
    """
    def __init__(self, terminology: Terminology):
        super(PartialMatchNCBISieve, self).__init__(terminology)

    @property
    def name(self) -> str:
        return "Partial Match Sieve"

    def apply(self, entity: SieveBasedEntity) -> Optional[str]:
        f_id = self._partial_match(entity.text, entity.text.split())
        if f_id is None:
            stemmed = self.text_processor.get_stemmed_phrase(entity.text)
            return self._partial_match(stemmed, stemmed.split())
        return f_id

    def _init_candidate_maps(self):
        self.cui_candidate_matching_tokens_count_map: Dict[str, int] = {}
        self.cui_candidate_length_map: Dict[str, int] = {}

    def _partial_match(self, phrase: str, tokens: List[str]) -> Optional[str]:
        partial_matched_phrases: Set[str] = set()
        self._init_candidate_maps()
        for token in tokens:
            if token in self.text_processor.stopwords:
                continue
            candidate_phrases: Optional[Set[str]] = None
            if token in self.terminology.token_to_name_map:
                candidate_phrases = self.terminology.token_to_name_map[token]
            if candidate_phrases is None:
                continue
            candidate_phrases.difference_update(partial_matched_phrases)
            self._ncbi_partial_match(phrase, candidate_phrases, partial_matched_phrases)
        return self._get_cui()

    def _ncbi_partial_match(self, phrase: str, candidate_phrases: Set[str], partial_matched_phrases: Set[str]):
        for candidate in candidate_phrases:
            partial_matched_phrases.add(candidate)
            count = self.text_processor.get_matching_tokens_count(phrase, candidate)
            cui = next(iter(self.terminology.name_to_cui_map[candidate]))

            if cui in self.cui_candidate_matching_tokens_count_map:
                old_count = self.cui_candidate_matching_tokens_count_map[cui]
                if old_count <= count:
                    new_candidate_len = len(candidate.split())
                    if old_count < count or (old_count == count and new_candidate_len < self.cui_candidate_length_map[cui]):
                        self.cui_candidate_matching_tokens_count_map[cui] = count
                        self.cui_candidate_length_map[cui] = new_candidate_len
            else:
                self.cui_candidate_matching_tokens_count_map[cui] = count
                self.cui_candidate_length_map[cui] = len(candidate.split())

    def _get_cui(self) -> Optional[str]:
        cui = None
        max_matched_tokens_count = -1
        max_cui_set: Set[str] = set()
        for candidate, matched_tokens_count in self.cui_candidate_matching_tokens_count_map.items():
            if matched_tokens_count == max_matched_tokens_count:
                max_cui_set.add(candidate)
            elif matched_tokens_count > max_matched_tokens_count:
                max_matched_tokens_count = matched_tokens_count
                max_cui_set = set()
                max_cui_set.add(candidate)
        if len(max_cui_set) == 1:
            return next(iter(max_cui_set))
        else:
            min_candidate_length = 1000
            for candidate_cui in max_cui_set:
                length = self.cui_candidate_length_map[candidate_cui]
                # Prefer D- over C-
                if length < min_candidate_length or (length == min_candidate_length and candidate_cui.startswith('D')):
                    min_candidate_length = length
                    cui = candidate_cui
        return cui
