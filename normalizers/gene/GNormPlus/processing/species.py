import re
from typing import List, Tuple, Dict, Set, Pattern

from nltk import tokenize

from common.models.bio_entities import SpeciesMention
from normalizers.gene.GNormPlus.models.paper import GNormPaper, GNormSpeciesAnnotation, SpeciesAnnotationPlacement, GNormGeneMention, \
    GNormPassage
from normalizers.gene.GNormPlus.util.re_patterns import SPECIES_PATTERN

HUMAN_ID = '9606'
TaxonomyFrequency = Dict[str, float]
HumanViruses = Set[str]
GeneWithoutSpPrefix = Set[str]
PrefixMap = Dict[str, Pattern[str]]

SENTENCE_TOKENIZER = tokenize.PunktSentenceTokenizer()


def assign_species(paper: GNormPaper, taxonomy_frequency: TaxonomyFrequency, human_viruses: HumanViruses,
                   gene_without_sp_prefix: GeneWithoutSpPrefix, prefix_map: PrefixMap):
    species_to_num_hash: Dict[str, float] = {}
    for passage in paper.passages:  # type: GNormPassage
        for species in passage.species:  # type: SpeciesMention
            match = re.match(SPECIES_PATTERN, species.id)
            if match:
                ID = match.group(1)
                weight = 1.0
                if passage.name == 'title':
                    weight = 2.0

                if ID in species_to_num_hash:
                    species_to_num_hash[ID] += weight
                else:
                    if ID in taxonomy_frequency:
                        species_to_num_hash[ID] = taxonomy_frequency[ID] + weight
                    else:
                        species_to_num_hash[ID] = weight

                    if ID in human_viruses:
                        if HUMAN_ID in species_to_num_hash:
                            species_to_num_hash[HUMAN_ID] += weight
                        else:
                            species_to_num_hash[HUMAN_ID] = taxonomy_frequency[HUMAN_ID] + weight

    major_species = HUMAN_ID
    max_species = .0
    for ID, freq in species_to_num_hash.items():  # type: str, float
        if freq > max_species:
            major_species = ID
            max_species = freq

    for passage in paper.passages:  # type: GNormPassage
        sentence_offsets: List[Tuple[int, int]] = list(SENTENCE_TOKENIZER.span_tokenize(passage.context))

        for gene in passage.genes:  # type: GNormGeneMention
            mention = gene.text.split('|')[0]  # Only use the first term to detect species

            # Prefix
            if mention not in gene_without_sp_prefix:
                for tax_id, prefix_pattern in prefix_map.items():  # type: str, Pattern[str]
                    match = re.match(prefix_pattern, mention)
                    if match:
                        mention_without_prefix = match.group(2)
                        gene.text += f'|{mention_without_prefix}'
                        gene.tax_id = GNormSpeciesAnnotation(tax_id, SpeciesAnnotationPlacement.PREFIX)
                        break

            if gene.tax_id:
                continue

            start = gene.location.start
            end = gene.location.end

            target_sentence = 0
            for i, (s_start, s_end) in enumerate(sentence_offsets):  # type: int, int, int
                if s_start <= start <= s_end:
                    target_sentence = i
                    break

            s_start, s_end = sentence_offsets[target_sentence]
            # Left
            closest_species_start = 0
            for sp in passage.species:  # type: SpeciesMention
                sp_start = sp.location.start
                match = re.match(SPECIES_PATTERN, sp.id)
                if match:
                    tax_id = match.group(1)
                    if start >= sp_start >= s_start and sp_start > closest_species_start:
                        closest_species_start = sp_start
                        gene.tax_id = GNormSpeciesAnnotation(tax_id, SpeciesAnnotationPlacement.LEFT)

            if gene.tax_id:
                continue

            # Right
            closest_species_end = 1_000_000
            for sp in passage.species:  # type: SpeciesMention
                sp_end = sp.location.end
                match = re.match(SPECIES_PATTERN, sp.id)
                if match:
                    tax_id = match.group(1)
                    if end <= sp_end <= s_end and sp_end < closest_species_end:
                        closest_species_end = sp_end
                        gene.tax_id = GNormSpeciesAnnotation(tax_id, SpeciesAnnotationPlacement.RIGHT)

            if gene.tax_id:
                continue

            gene.tax_id = GNormSpeciesAnnotation(major_species, SpeciesAnnotationPlacement.FOCUS)
