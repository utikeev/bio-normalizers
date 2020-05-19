from collections import defaultdict
from typing import Dict, List, Set

from common.util.files import process_file
from normalizers.disease.SieveBased.models.entities import SieveBasedDisease
from normalizers.disease.SieveBased.util.text_processor import TextProcessor


class Terminology:
    def __init__(self, terminology_path: str, text_processor: TextProcessor):
        self.terminology_path: str = terminology_path
        self.text_processor: TextProcessor = text_processor
        self.name_to_cui_map: Dict[str, List[str]] = defaultdict(list)
        self.cui_to_name_map: Dict[str, List[str]] = defaultdict(list)
        self.stemmed_name_to_cui_map: Dict[str, List[str]] = defaultdict(list)
        self.cui_to_stemmed_name_map: Dict[str, List[str]] = defaultdict(list)
        self.token_to_name_map: Dict[str, Set[str]] = defaultdict(set)
        self.normalized_name_to_cui_map: Dict[str, List[str]] = defaultdict(list)
        self.stemmed_normalized_name_to_cui_map: Dict[str, List[str]] = defaultdict(list)
        self.simple_name_to_cui_map: Dict[str, List[str]] = defaultdict(list)

    def load(self, *, verbose: bool = False):
        process_file(self.terminology_path, self._load_terminology, verbose=verbose, message='Loading terminology...')

    def _load_terminology(self, line: str):
        cui, aliases_str = line.split('||')  # type: str, str
        aliases = aliases_str.lower().split('|')
        for alias in aliases:
            self._put_to_maps(cui, alias)

    def _put_to_maps(self, cui: str, alias: str):
        alias = alias.replace(',', '')
        self.name_to_cui_map[alias].append(cui)
        self.cui_to_name_map[cui].append(alias)

        stemmed_concept_name = self.text_processor.get_stemmed_phrase(alias)
        self.stemmed_name_to_cui_map[stemmed_concept_name].append(cui)
        self.cui_to_stemmed_name_map[cui].append(stemmed_concept_name)

        tokens = alias.split()
        for token in tokens:
            if token not in self.text_processor.stopwords:
                self.token_to_name_map[token].add(alias)

        if len(tokens) == 3:
            new_phrase = f'{tokens[0]} {tokens[2]}'
            self.simple_name_to_cui_map[new_phrase].append(cui)
            new_phrase = f'{tokens[1]} {tokens[2]}'
            self.simple_name_to_cui_map[new_phrase].append(cui)

    def store_normalized_disease(self, disease: SieveBasedDisease):
        if disease.normalizing_sieve_level == 2 and disease.long_form is None:
            return

        normalized_key = disease.long_form if disease.normalizing_sieve_level == 2 else disease.text
        stemmed_normalized_key = self.text_processor.get_stemmed_phrase(disease.long_form) if disease.normalizing_sieve_level == 2 \
            else disease.stemmed_name

        self.normalized_name_to_cui_map[normalized_key] = disease.id
        self.stemmed_normalized_name_to_cui_map[stemmed_normalized_key] = disease.id
