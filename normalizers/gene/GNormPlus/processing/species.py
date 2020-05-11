import re
from typing import List, Tuple, Dict, Set

from nltk import tokenize

from normalizers.gene.GNormPlus.models.paper import Paper, SpeciesAnnotation, SpeciesAnnotationPlacement

HUMAN_ID = '9606'
TaxonomyFrequency = Dict[str, float]
HumanViruses = Set[str]
GeneWithoutSpPrefix = Set[str]
PrefixMap = Dict[str, str]

SENTENCE_TOKENIZER = tokenize.PunktSentenceTokenizer()


def assign_species(paper: Paper, taxonomy_frequency: TaxonomyFrequency, human_viruses: HumanViruses,
                   gene_without_sp_prefix: GeneWithoutSpPrefix, prefix_map: PrefixMap):
    species_to_num_hash: Dict[str, float] = {}
    for passage in paper.passages:
        for species in passage.species:
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
    for ID, freq in species_to_num_hash.items():
        if freq > max_species:
            major_species = ID
            max_species = freq

    for passage in paper.passages:
        sentence_offsets: List[Tuple[int, int]] = list(SENTENCE_TOKENIZER.span_tokenize(passage.context))

        for annotation in passage.annotations:
            mention = annotation.text.split('|')[0]  # Only use the first term to detect species

            # Prefix
            if mention not in gene_without_sp_prefix:
                for tax_id, prefix in prefix_map.items():
                    match = re.match(rf'^({prefix})([A-Z].*)$', mention)
                    if match:
                        mention_without_prefix = match.group(2)
                        annotation.text += f'|{mention_without_prefix}'
                        annotation.tax_id = SpeciesAnnotation(tax_id, SpeciesAnnotationPlacement.PREFIX)
                        break

            start = annotation.location.start
            end = annotation.location.end

            target_sentence = 0
            for i, (s_start, s_end) in enumerate(sentence_offsets):
                if s_start <= start <= s_end:
                    target_sentence = i
                    break

            s_start, s_end = sentence_offsets[target_sentence]
            closest_species_start = 0
            for sp in passage.species:  # Left
                sp_start = sp.location.start
                match = re.match(r'\**([0-9]+)$', sp.id)
                if match:
                    tax_id = match.group(1)
                    if start >= sp_start >= s_start and sp_start > closest_species_start:
                        closest_species_start = sp_start
                        annotation.tax_id = SpeciesAnnotation(tax_id, SpeciesAnnotationPlacement.LEFT)

            if not annotation.tax_id:
                closest_species_end = 1_000_000
                for sp in passage.species:  # Right
                    sp_end = sp.location.end
                    match = re.match(r'\**([0-9]+)$', sp.id)
                    if match:
                        tax_id = match.group(1)
                        if end <= sp_end <= s_end and sp_end < closest_species_end:
                            closest_species_end = sp_end
                            annotation.tax_id = SpeciesAnnotation(tax_id, SpeciesAnnotationPlacement.RIGHT)
            # Co-occurring
            if not annotation.tax_id:
                annotation.tax_id = SpeciesAnnotation(major_species, SpeciesAnnotationPlacement.FOCUS)
