import abc
from enum import Enum
from typing import Optional

from common.models.util import Location


class BioEntityType(Enum):
    GENE = 'GENE'
    SPECIES = 'SPECIES'
    DISEASE = 'DISEASE'
    CHEMICAL = 'CHEMICAL'


class BioEntity(abc.ABC):
    def __init__(self, location: Location, text: str):
        self.location = location
        self.text = text
        self.id: Optional[str] = None

    def __str__(self):
        return f'{self.location}\t{self.text}\t{self.id}'

    def __repr__(self):
        return str(self)

    @property
    @abc.abstractmethod
    def e_type(self) -> BioEntityType:
        pass


class SpeciesMention(BioEntity):
    @property
    def e_type(self) -> BioEntityType:
        return BioEntityType.SPECIES


class GeneMention(BioEntity):
    @property
    def e_type(self) -> BioEntityType:
        return BioEntityType.GENE


class DiseaseMention(BioEntity):
    @property
    def e_type(self) -> BioEntityType:
        return BioEntityType.DISEASE


class ChemicalMention(BioEntity):
    @property
    def e_type(self) -> BioEntityType:
        return BioEntityType.CHEMICAL
