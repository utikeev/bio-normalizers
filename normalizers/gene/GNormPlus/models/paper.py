from enum import Enum
from typing import List, Dict


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


class AnnotationType(Enum):
    GENE = 'GENE'
    CELL = 'CELL'
    FAMILY_NAME = 'FAMILY_NAME'
    DOMAIN_MOTIF = 'DOMAIN_MOTIF'


class Annotation:
    def __init__(self, location: Location, text: str, a_type: AnnotationType):
        self.location = location
        self.text = text
        self.type = a_type
        # TODO: assign species
        self.tax_id = '9606'
        self.id = None

    def __str__(self):
        return f'{self.location}\t{self.text}\t{self.type}\t{self.tax_id}\t{self.id}'

    def __repr__(self):
        return str(self)


class Passage:
    def __init__(self, name: str, context: str, annotations: List[Annotation]):
        self.name = name
        self.context = context
        self.annotations = annotations

    def __str__(self):
        return f'{self.name}\t{self.context}\t{" ".join([str(a) for a in self.annotations])}'

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
