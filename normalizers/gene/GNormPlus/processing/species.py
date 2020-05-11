import re
from typing import List, Tuple, Dict, Set

from nltk import tokenize

from normalizers.gene.GNormPlus.models.paper import Paper, SpeciesAnnotation, SpeciesAnnotationPlacement, Passage, Species, GeneAnnotation

HUMAN_ID = '9606'
TaxonomyFrequency = Dict[str, float]
HumanViruses = Set[str]
GeneWithoutSpPrefix = Set[str]
PrefixMap = Dict[str, str]

SENTENCE_TOKENIZER = tokenize.PunktSentenceTokenizer()


def assign_species(paper: Paper, taxonomy_frequency: TaxonomyFrequency, human_viruses: HumanViruses,
                   gene_without_sp_prefix: GeneWithoutSpPrefix, prefix_map: PrefixMap):
    species_to_num_hash: Dict[str, float] = {}
    for passage in paper.passages:  # type: Passage
        for species in passage.species:  # type: Species
            match = re.match(r'\**([0-9]+)$', species.id)
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

    for passage in paper.passages:  # type: Passage
        sentence_offsets: List[Tuple[int, int]] = list(SENTENCE_TOKENIZER.span_tokenize(passage.context))

        for gene in passage.genes:  # type: GeneAnnotation
            mention = gene.text.split('|')[0]  # Only use the first term to detect species

            # Prefix
            if mention not in gene_without_sp_prefix:
                for tax_id, prefix in prefix_map.items():  # type: str, str
                    match = re.match(rf'^({prefix})([A-Z].*)$', mention)
                    if match:
                        mention_without_prefix = match.group(2)
                        gene.text += f'|{mention_without_prefix}'
                        gene.tax_id = SpeciesAnnotation(tax_id, SpeciesAnnotationPlacement.PREFIX)
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
            for sp in passage.species:  # type: Species
                sp_start = sp.location.start
                match = re.match(r'\**([0-9]+)$', sp.id)
                if match:
                    tax_id = match.group(1)
                    if start >= sp_start >= s_start and sp_start > closest_species_start:
                        closest_species_start = sp_start
                        gene.tax_id = SpeciesAnnotation(tax_id, SpeciesAnnotationPlacement.LEFT)

            if gene.tax_id:
                continue

            # Right
            closest_species_end = 1_000_000
            for sp in passage.species:  # type: Species
                sp_end = sp.location.end
                match = re.match(r'\**([0-9]+)$', sp.id)
                if match:
                    tax_id = match.group(1)
                    if end <= sp_end <= s_end and sp_end < closest_species_end:
                        closest_species_end = sp_end
                        gene.tax_id = SpeciesAnnotation(tax_id, SpeciesAnnotationPlacement.RIGHT)

            if gene.tax_id:
                continue

            gene.tax_id = SpeciesAnnotation(major_species, SpeciesAnnotationPlacement.FOCUS)
