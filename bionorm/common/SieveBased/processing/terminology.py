from collections import defaultdict
from typing import Dict, Set

from bionorm.common.SieveBased.models import SieveBasedEntity
from bionorm.common.SieveBased.util import TextProcessor
from bionorm.common.util import process_file


class Terminology:
    """Wrapper around terminology dictionary.

    Contains mapping from ID to list of aliases of entity. Also has some additional helper maps.

    Notes:
        After creation of terminology call load_data() to load all of the data.
        This is also done by load_data() of SieveBasedNormalizer.
    """
    def __init__(self, terminology_path: str, text_processor: TextProcessor):
        """
        Args:
            terminology_path (str):
                Path to terminology dictionary.
            text_processor (TextProcessor):
                Text processor to use.
        """
        self.terminology_path: str = terminology_path
        self.text_processor: TextProcessor = text_processor
        self.name_to_cui_map: Dict[str, Set[str]] = defaultdict(set)
        self.cui_to_name_map: Dict[str, Set[str]] = defaultdict(set)
        self.stemmed_name_to_cui_map: Dict[str, Set[str]] = defaultdict(set)
        self.cui_to_stemmed_name_map: Dict[str, Set[str]] = defaultdict(set)
        self.token_to_name_map: Dict[str, Set[str]] = defaultdict(set)
        self.normalized_name_to_cui_map: Dict[str, Set[str]] = defaultdict(set)
        self.stemmed_normalized_name_to_cui_map: Dict[str, Set[str]] = defaultdict(set)
        self.simple_name_to_cui_map: Dict[str, Set[str]] = defaultdict(set)

    def load_data(self, *, verbose: bool = False):
        """Loads data in terminology.

        Args:
            verbose (:obj:`bool`, defaults to :obj:`False`):
                Whether to output verbose information about loading.
        """
        process_file(self.terminology_path, self._load_terminology, verbose=verbose, message='Loading terminology...')

    def _load_terminology(self, line: str):
        cui, aliases_str = line.split('||')  # type: str, str
        aliases = aliases_str.lower().split('|')
        for alias in aliases:
            self._put_to_maps(cui, alias)
            cleaned_alias = alias.replace(',', '')
            if cleaned_alias != alias:
                self._put_to_maps(cui, alias.replace(',', ''))

    def _put_to_maps(self, cui: str, alias: str):
        self.name_to_cui_map[alias].add(cui)
        self.cui_to_name_map[cui].add(alias)

        stemmed_concept_name = self.text_processor.get_stemmed_phrase(alias)
        self.stemmed_name_to_cui_map[stemmed_concept_name].add(cui)
        self.cui_to_stemmed_name_map[cui].add(stemmed_concept_name)

        tokens = alias.split()
        for token in tokens:
            if token not in self.text_processor.stopwords:
                self.token_to_name_map[token].add(alias)

        if len(tokens) == 3:
            new_phrase = f'{tokens[0]} {tokens[2]}'
            self.simple_name_to_cui_map[new_phrase].add(cui)
            new_phrase = f'{tokens[1]} {tokens[2]}'
            self.simple_name_to_cui_map[new_phrase].add(cui)

    def store_normalized_entity(self, entity: SieveBasedEntity):
        """Store already normalized entity to have it in cache.

        Args:
            entity (SieveBasedEntity):
                Entity to save in normalized maps.
        """
        if entity.normalizing_sieve_level == 2 and entity.long_form is None:
            return

        normalized_key = entity.long_form if entity.normalizing_sieve_level == 2 else entity.text
        stemmed_normalized_key = self.text_processor.get_stemmed_phrase(entity.long_form) if entity.normalizing_sieve_level == 2 \
            else entity.stemmed_name

        self.normalized_name_to_cui_map[normalized_key] = entity.id
        self.stemmed_normalized_name_to_cui_map[stemmed_normalized_key] = entity.id

    def clear_normalized_entities(self):
        """Clear normalized entities after processing the article, as they may be multiple meaning abbreviations.
        """
        self.normalized_name_to_cui_map.clear()
        self.stemmed_normalized_name_to_cui_map.clear()
