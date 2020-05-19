import abc
from typing import Optional

from normalizers.disease.SieveBased.models.entities import SieveBasedDisease
from normalizers.disease.SieveBased.processing.terminology import Terminology


class Sieve(abc.ABC):
    def __init__(self, terminology: Terminology):
        self.terminology = terminology
        self.text_processor = terminology.text_processor

    @abc.abstractmethod
    def apply(self, disease: SieveBasedDisease) -> Optional[str]:
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass
