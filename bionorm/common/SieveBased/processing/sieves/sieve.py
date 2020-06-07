import abc
from typing import Optional

from bionorm.common.SieveBased.models import SieveBasedEntity
from bionorm.common.SieveBased.processing import Terminology


class Sieve(abc.ABC):
    """Sieve is the block, which uses some heuristic to try normalizing entities.

    apply() method of sieve can add some of the additional aliases for entities, which may help further sieves to find ID.
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
    def apply(self, entity: SieveBasedEntity) -> Optional[str]:
        """Try to normalize entity.

        Args:
            entity (SieveBasedEntity):
                Entity to normalize.

        Returns:
            ID in terminology matching the entity alias or None if not found.
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
