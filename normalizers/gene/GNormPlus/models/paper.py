from enum import Enum
from typing import List, Dict, Optional


class Location:
    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    def __str__(self):
        return f'[{self.start}, {self.end}]'

    def __repr__(self):
        return str(self)


class Abbreviation:
    def __init__(self, long_form: str, short_form: str):
        self.long_form = long_form
        self.short_form = short_form


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


class SpeciesAnnotation:
    def __init__(self, s_id: str, placement: SpeciesAnnotationPlacement):
        self.id = s_id
        self.placement = placement

    def __str__(self):
        return f'{self.placement}: {self.id}'

    def __repr__(self):
        return str(self)


class GeneAnnotation:
    def __init__(self, location: Location, text: str):
        self.location = location
        self.text = text
        self.type = GeneType.GENE
        self.tax_id: Optional[SpeciesAnnotation] = None
        self.id: Optional[str] = None

    def __str__(self):
        return f'{self.location}\t{self.text}\t{self.type}\t{self.tax_id}\t{self.id}'

    def __repr__(self):
        return str(self)


class Species:
    def __init__(self, location: Location, text: str, s_id: str):
        self.location = location
        self.text = text
        self.id = s_id

    def __str__(self):
        return f'{self.location}\t{self.text}\t{self.id}'

    def __repr__(self):
        return str(self)


class Passage:
    def __init__(self, name: str, context: str, genes: List[GeneAnnotation], species: Optional[List[Species]] = None):
        self.name = name
        self.context = context
        self.genes = genes
        self.species: List[Species] = species or []

    def __str__(self):
        return f'{self.name}\t{self.context}\t{" ".join([str(a) for a in self.genes])}'

    def __repr__(self):
        return str(self)


class Paper:
    def __init__(self, pmid: str, passages: List[Passage], abbreviations: List[Abbreviation]):
        self.pmid = pmid
        self.passages = passages
        self.abbreviations = abbreviations
        self.abb_sf_to_lf: Dict[str, str] = {}
        self.abb_lf_to_sf: Dict[str, str] = {}
        for abbreviation in self.abbreviations:
            sf = abbreviation.short_form.lower()
            lf = abbreviation.long_form.lower()
            self.abb_sf_to_lf[sf] = lf
            self.abb_lf_to_sf[lf] = sf

        self.chromosome_hash = set()

    def __str__(self):
        passages = "\n".join([str(p) for p in self.passages])
        return f'{self.pmid}\t{passages}'

    def __repr__(self):
        return str(self)
