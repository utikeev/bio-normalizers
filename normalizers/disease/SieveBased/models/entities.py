from typing import Optional, Set

from common.models.bio_entities import DiseaseMention
from normalizers.disease.SieveBased.util.text_processor import TextProcessor

CUI_LESS = 'CUI-less'


class SieveBasedDisease:
    def __init__(self, disease: DiseaseMention, text_processor: TextProcessor, long_form: Optional[str] = None):
        self.__disease = disease
        self.__disease.text = text_processor.correct_spelling(self.text.lower().strip())
        self.stemmed_name = text_processor.get_stemmed_phrase(self.text)
        self.normalizing_sieve_level = 0
        self.names_knowledge_base: Set[str] = set()
        self.stemmed_names_knowledge_base: Set[str] = set()
        self.long_form: Optional[str] = long_form

    @property
    def text(self):
        return self.__disease.text

    @property
    def id(self):
        return self.__disease.id

    @id.setter
    def id(self, value):
        self.__disease.id = value
