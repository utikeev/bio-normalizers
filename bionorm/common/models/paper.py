from typing import List, Dict

from bionorm.common.models.bio_entities import GeneMention, SpeciesMention, DiseaseMention, ChemicalMention, BioEntity, Abbreviation


class Passage:
    def __init__(self, name: str, context: str, *,
                 genes: List[GeneMention] = None,
                 species: List[SpeciesMention] = None,
                 diseases: List[DiseaseMention] = None,
                 chemicals: List[ChemicalMention] = None
                 ):
        self.name = name
        self.context = context
        self.genes: List[GeneMention] = genes or []
        self.species: List[SpeciesMention] = species or []
        self.diseases: List[DiseaseMention] = diseases or []
        self.chemicals: List[ChemicalMention] = chemicals or []

    def __str__(self):
        all_mentions: List[BioEntity] = self.genes + self.species + self.diseases + self.chemicals
        mentions_str = "\n".join([str(a) for a in all_mentions])
        return f'{self.name}\t{self.context}\t{mentions_str}'

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

    def __str__(self):
        passages = "\n".join([str(p) for p in self.passages])
        return f'{self.pmid}\t{passages}'

    def __repr__(self):
        return str(self)
