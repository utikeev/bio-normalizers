from collections import defaultdict
from typing import List, Dict, Optional, Set

import nltk
from nltk import StemmerI
from nltk.corpus import stopwords

from common.SieveBased.config.config import SieveBasedConfig
from common.util.files import process_file


class TextProcessor:
    """Text processor used in sieves.

    Notes:
        After creation of text processor call load_data() to load all of the data.
        This is also done by load_data() of SieveBasedNormalizer.
    """
    def __init__(self, config: SieveBasedConfig):
        """
        Args:
            config (SieveBasedConfig):
                Config with the text processor options.
        """
        self.config: SieveBasedConfig = config
        self.stemmer: StemmerI = config.stemmer_constructor()
        self.stopwords: Set[str] = set()
        self.spell_check_map: Dict[str, str] = {}
        self.prepositions: List[str] = []
        self.digit_to_word_map: Dict[str, List[str]] = defaultdict(list)
        self.word_to_digit_map: Dict[str, str] = {}
        self.suffix_map: Dict[str, List[str]] = defaultdict(list)
        self.prefix_map: Dict[str, str] = {}
        self.affix_map: Dict[str, str] = {}
        self.singular_synonyms: List[str] = []
        self.plural_synonyms: List[str] = []

    def load_data(self, *, verbose=False):
        """Loads data in processor maps.

        Args:
            verbose (:obj:`bool`, defaults to :obj:`False`):
                Whether to output verbose information about loading.
        """
        if self.config.use_nltk_stopwords:
            nltk.download('stopwords', quiet=not verbose)
            self.stopwords = set(stopwords.words('english'))
        else:
            process_file(self.config.stopwords_path, self._load_stopwords, verbose=verbose, message='Loading stopwords...')

        process_file(self.config.spell_check_map_path, self._load_spellcheck, verbose=verbose, message='Loading spellcheck map...')
        process_file(self.config.prepositions_path, self._load_prepositions, verbose=verbose, message='Loading prepositions...')
        process_file(self.config.digit_map_path, self._load_digit_map, verbose=verbose, message='Loading digit map...')
        process_file(self.config.suffix_map_path, self._load_suffix_map, verbose=verbose, message='Loading suffix map...')
        process_file(self.config.prefix_map_path, self._load_prefix_map, verbose=verbose, message='Loading prefix map...')
        process_file(self.config.affix_map_path, self._load_affix_map, verbose=verbose, message='Loading affix map...')
        process_file(self.config.singular_synonyms_path, self._load_singular_synonyms, verbose=verbose, message='Loading singular '
                                                                                                                'synonyms...')
        process_file(self.config.plural_synonyms_path, self._load_plural_synonyms, verbose=verbose, message='Loading plural synonyms...')

    def _load_stopwords(self, line: str):
        self.stopwords.add(line)

    def _load_spellcheck(self, line: str):
        error, correct = line.split('||')
        self.spell_check_map[error] = correct

    def _load_prepositions(self, line: str):
        self.prepositions.append(line)

    def _load_digit_map(self, line: str):
        digit, word = line.split('||')
        self.digit_to_word_map[digit].append(word)
        self.word_to_digit_map[word] = digit

    def _load_suffix_map(self, line: str):
        parts = line.split('||')
        suffix = parts[0]
        if len(parts) == 2:
            replace = parts[1]
        else:
            replace = ''
        self.suffix_map[suffix].append(replace)

    def _load_prefix_map(self, line: str):
        parts = line.split('||')
        prefix = parts[0]
        if len(parts) == 2:
            replace = parts[1]
        else:
            replace = ''
        self.prefix_map[prefix] = replace

    def _load_affix_map(self, line: str):
        affix, replace = line.split('||')
        self.affix_map[affix] = replace

    def _load_singular_synonyms(self, line: str):
        self.singular_synonyms.append(line)

    def _load_plural_synonyms(self, line: str):
        self.plural_synonyms.append(line)

    def get_stemmed_phrase(self, string: str) -> str:
        """Stem phrase excluding stopwords from stemming.

        Args:
            string (str):
                String to stem.

        Returns:
            Stemmed string.
        """
        stemmed: List[str] = []
        tokens = string.split()
        for token in tokens:
            if token in self.stopwords:
                stemmed.append(token)
            else:
                stemmed_token: str = self.stemmer.stem(token).strip()
                if stemmed_token == '':
                    stemmed_token = token
                stemmed.append(stemmed_token)
        return ' '.join(stemmed)

    def correct_spelling(self, string: str) -> str:
        """Corrects some of the often mistakes in bio texts.

        Args:
            string (str):
                String to fix mistakes in.
        Returns:
            Corrected string.
        """
        corrected: List[str] = []
        string.replace('--', ' ')
        tokens = string.split()
        for token in tokens:
            if token in self.spell_check_map:
                token = self.spell_check_map[token]
            corrected.append(token)
        return ' '.join(corrected)

    def get_preposition(self, string: str) -> Optional[str]:
        """Get the first preposition of the string.

        Args:
            string (str):
                String to look preposition in.
        Returns:
            Preposition if found. None, otherwise.
        """
        for p in self.prepositions:
            if f' {p} ' in string:
                return p
        return None

    @staticmethod
    def get_token_substring(tokens: List[str], begin: int, end: int) -> str:
        """Get substring by word borders.

        Args:
            tokens (List[str]):
                List of words.
            begin (int):
                Begin offset.
            end (int):
                End offset.

        Returns:
            Text from begin-th to end-th word.
        """
        return ' '.join(tokens[begin:end])

    @staticmethod
    def get_token_index(tokens: List[str], token: str) -> Optional[int]:
        """Find index of token in the tokens list.

        Args:
            tokens (List[str]):
                List of words.
            token (str):
                Word to find.

        Returns:
            Index of token in tokens or None if it isn't there.
        """
        try:
            return tokens.index(token)
        except ValueError:
            return None

    def get_suffix(self, string: str) -> Optional[str]:
        """Get suffix of the string.

        Args:
            string (str):
                String to find suffix in.

        Returns:
            Suffix of the string or None if it isn't found.
        """
        for suffix in self.suffix_map.keys():
            if string.endswith(suffix):
                return suffix
        return None

    def get_prefix(self, string: str) -> Optional[str]:
        """Get prefix of the string.

        Args:
            string (str):
                String to find prefix in.

        Returns:
            Prefix of the string or None if it isn't found.
        """
        for prefix in self.prefix_map.keys():
            if string.startswith(prefix):
                return prefix
        return None

    def get_affix(self, string: str) -> Optional[str]:
        """Get affix of the string.

        Args:
            string (str):
                String to find affix in.

        Returns:
            Affix of the string or None if it isn't found.
        """
        for affix in self.affix_map.keys():
            if affix in string:
                return affix
        return None

    def get_matching_tokens_count(self, string1: str, string2: str) -> int:
        """Count amount of matching unique tokens in both strings, excluding stopwords.

        Args:
            string1 (str):
                First string.
            string2 (str):
                Second string.

        Returns:
            Amount of common tokens without stopwords.
        """
        tokens1 = set(string1.split())
        tokens2 = set(string2.split())
        intersecting = tokens1.intersection(tokens2).difference(self.stopwords)
        return len(intersecting)
