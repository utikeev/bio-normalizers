from enum import Enum
from typing import List, Dict, Optional

from bionorm.common.models import GeneMention, SpeciesMention, Paper, Passage


class GeneType(Enum):
    GENE = 'GENE'
    CELL = 'CELL'
    FAMILY_NAME = 'FAMILY_NAME'
    DOMAIN_MOTIF = 'DOMAIN_MOTIF'


class SpeciesAnnotationPlacement:
    FOCUS = 'Focus'
    RIGHT = 'Right'
    LEFT = 'Left'
    PREFIX = 'Prefix'
    FALLBACK = 'Fallback'


class GNormSpeciesAnnotation:
    def __init__(self, s_id: str, placement: SpeciesAnnotationPlacement):
        self.id = s_id
        self.placement = placement

    def __str__(self):
        return f'{self.placement}: {self.id}'

    def __repr__(self):
        return str(self)


class GNormGeneMention:
    def __init__(self, gene: GeneMention):
        self.gene = gene
        self.text = self.gene.text
        self.type = GeneType.GENE
        self.tax_id: Optional[GNormSpeciesAnnotation] = None

    @property
    def location(self):
        return self.gene.location

    @property
    def id(self):
        return self.gene.id

    @id.setter
    def id(self, value):
        self.gene.id = value

    def __str__(self):
        return f'{self.location}\t{self.text}\t{self.type}\t{self.tax_id}\t{self.id}'

    def __repr__(self):
        return str(self)


class GNormPassage:
    def __init__(self, passage: Passage):
        self.passage = passage
        self.genes = list(map(lambda gene: GNormGeneMention(gene), passage.genes))

    @property
    def name(self) -> str:
        return self.passage.name

    @property
    def context(self) -> str:
        return self.passage.context

    @property
    def species(self) -> List[SpeciesMention]:
        return self.passage.species


class GNormPaper:
    def __init__(self, paper: Paper):
        self.paper = paper
        self.passages = list(map(lambda passage: GNormPassage(passage), paper.passages))
        self.chromosome_hash = set()

    @property
    def pmid(self) -> str:
        return self.paper.pmid

    @property
    def abb_sf_to_lf(self) -> Dict[str, str]:
        return self.paper.abb_sf_to_lf

    @property
    def abb_lf_to_sf(self) -> Dict[str, str]:
        return self.paper.abb_lf_to_sf

    def __str__(self):
        return str(self.paper)
