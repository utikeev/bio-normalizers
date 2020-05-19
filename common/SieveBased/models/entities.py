from typing import Optional, Set

from common.SieveBased.util.text_processor import TextProcessor
from common.models.bio_entities import BioEntity

CUI_LESS = 'CUI-less'


class SieveBasedEntity:
    """BioEntity wrapper for sieve-based normalizer.

    Contains stemmed name, the level of normalizer which was used to normalize, known aliases.
    """
    def __init__(self, entity: BioEntity, text_processor: TextProcessor, long_form: Optional[str] = None):
        """
        Args:
            entity (BioEntity):
                Original entity.
            text_processor (TextProcessor):
                Text processor to operate with.
            long_form (:obj:`str`, defaults to :obj:`None`):
                Long form if entity is abbreviation.
        """
        self.__entity = entity
        self.text = text_processor.correct_spelling(self.__entity.text.lower().strip())
        self.stemmed_name = text_processor.get_stemmed_phrase(self.text)
        self.normalizing_sieve_level = 0
        self.names_knowledge_base: Set[str] = set()
        self.stemmed_names_knowledge_base: Set[str] = set()
        self.long_form: Optional[str] = long_form

    @property
    def id(self):
        return self.__entity.id

    @id.setter
    def id(self, value):
        self.__entity.id = value
