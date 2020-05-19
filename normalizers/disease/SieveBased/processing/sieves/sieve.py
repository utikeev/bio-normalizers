import abc
from typing import Optional

from normalizers.disease.SieveBased.models.entities import SieveBasedDisease
from normalizers.disease.SieveBased.processing.terminology import Terminology


class Sieve(abc.ABC):
    """Sieve is the block, which uses some heuristic to try normalizing diseases.

    apply() method of sieve can add some of the additional aliases for disease, which may help further sieves to find ID.
    """
    def __init__(self, terminology: Terminology):
        """
        Args:
            terminology (Terminology):
                Terminology which is used by sieve.
        """
        self.terminology = terminology
        self.text_processor = terminology.text_processor

    @abc.abstractmethod
    def apply(self, disease: SieveBasedDisease) -> Optional[str]:
        """Try to normalize disease.

        Args:
            disease (SieveBasedDisease):
                Disease to normalize.

        Returns:
            ID in terminology matching the disease alias or None if not found.
        """
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Display name of sieve.

        Returns:
            String with sieve name.
        """
        pass
