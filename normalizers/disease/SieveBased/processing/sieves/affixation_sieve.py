from typing import Optional, Set, List

from normalizers.disease.SieveBased.models.entities import SieveBasedDisease
from normalizers.disease.SieveBased.processing.sieves.base_sieve import BaseSieve
from normalizers.disease.SieveBased.processing.terminology import Terminology


class AffixationSieve(BaseSieve):
    def __init__(self, terminology: Terminology):
        super(AffixationSieve, self).__init__(terminology)

    def apply(self, disease: SieveBasedDisease) -> Optional[str]:
        self._transform_name(disease)
        return self.normalize(disease.names_knowledge_base)

    def _transform_name(self, disease: SieveBasedDisease):
        transformed_names: Set[str] = set()
        for name in disease.names_knowledge_base:
            transformed_names.update(self._affix(name))
        disease.names_knowledge_base.update(transformed_names)

    def _affix(self, name: str) -> Set[str]:
        tokens = name.split()
        new_phrases = self._suffixation(tokens, name)
        new_phrases.update(self._prefixation(tokens))
        new_phrases.update(self._affixation(tokens))
        return new_phrases

    def _suffixation(self, tokens: List[str], name: str) -> Set[str]:
        return self._get_all_string_token_suffixation_combinations(tokens).union(self._get_uniform_string_token_suffixation(tokens, name))

    def _get_all_string_token_suffixation_combinations(self, tokens: List[str]) -> Set[str]:
        suffixated_phrases: List[str] = []
        for token in tokens:
            suffix = self.text_processor.get_suffix(token)
            for_suffixation = None if suffix is None else self.text_processor.suffix_map[suffix]
            if len(suffixated_phrases) == 0:
                if for_suffixation is None:
                    suffixated_phrases.append(token)
                else:
                    for s in for_suffixation:
                        suffixated_phrases.append(token.replace(suffix, s))
            else:
                if for_suffixation is None:
                    for i in range(len(suffixated_phrases)):
                        suffixated_phrases[i] = suffixated_phrases[i] + ' ' + token
                else:
                    temp_suffixated_phrases: List[str] = []
                    for phrase in suffixated_phrases:
                        for s in for_suffixation:
                            temp_suffixated_phrases.append(phrase + ' ' + token.replace(suffix, s))
                    suffixated_phrases = temp_suffixated_phrases
        return set(suffixated_phrases)

    def _get_uniform_string_token_suffixation(self, tokens: List[str], name: str) -> Set[str]:
        suffixated_phrases: Set[str] = set()
        for token in tokens:
            suffix = self.text_processor.get_suffix(token)
            for_suffixation = None if suffix is None else self.text_processor.suffix_map[suffix]
            if for_suffixation is None:
                continue
            for s in for_suffixation:
                suffixated_phrases.add(name.replace(suffix, s))
        return suffixated_phrases

    def _prefixation(self, tokens: List[str]) -> str:
        prefixated_tokens: List[str] = []
        for token in tokens:
            prefix = self.text_processor.get_prefix(token)
            new_token = token if prefix is None else token.replace(prefix, self.text_processor.prefix_map[prefix])
            prefixated_tokens.append(new_token)
        return ' '.join(prefixated_tokens)

    def _affixation(self, tokens: List[str]) -> str:
        affixated_tokens: List[str] = []
        for token in tokens:
            affix = self.text_processor.get_affix(token)
            new_token = token if affix is None else token.replace(affix, self.text_processor.affix_map[affix])
            affixated_tokens.append(new_token)
        return ' '.join(affixated_tokens)
