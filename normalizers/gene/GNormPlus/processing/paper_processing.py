import re
from typing import Dict

from normalizers.gene.GNormPlus.models.paper import GNormPaper, GeneType, Passage, GNormGeneMention
from normalizers.gene.GNormPlus.util.re_patterns import PREPROCESS_PATTERN0, PREPROCESS_PATTERN1, PREPROCESS_PATTERN2, PREPROCESS_PATTERN3, \
    PREPROCESS_PATTERN4, PREPROCESS_PATTERN5, PREPROCESS_PATTERN6, PREPROCESS_PATTERN7
from normalizers.gene.GNormPlus.util.trees import PrefixTree, FoundMention

_CELL_SUFFIX = '(cell|cells)'
_FAMILY_NAME_SUFFIX = '(disease|diseases|syndrome|syndromes|tumor|tumour|deficiency|dysgenesis|atrophy|frame|dystrophy|frame|factors|' \
                      'family|families|superfamily|superfamilies|subfamily|subfamilies|complex|genes|proteins)'
_DOMAIN_MOTIF_SUFFIX = '(domain|motif|domains|motifs|sequences)'

_DEFAULT_BOUNDARY_LEN = 15


def preprocess_paper(paper: GNormPaper, chromosome_tree: PrefixTree):
    mention_to_type: Dict[str, GeneType] = {}

    for passage in paper.passages:  # type: Passage
        for i, annotation in enumerate(passage.genes):  # type: GNormGeneMention
            mention = annotation.text.lower()
            m_type = annotation.type
            end = annotation.location.end
            trailing = passage.context[end: end + _DEFAULT_BOUNDARY_LEN]

            # Check suffix – Gene -> Family/Domain/Cell
            if re.match(f'.*{_CELL_SUFFIX}', mention) or re.match(_CELL_SUFFIX, trailing):
                m_type = GeneType.CELL
            elif re.match(f'.*{_FAMILY_NAME_SUFFIX}', mention) or re.match(_FAMILY_NAME_SUFFIX, trailing):
                m_type = GeneType.FAMILY_NAME
            elif re.match(f'.*{_DOMAIN_MOTIF_SUFFIX}', mention) or re.match(_DOMAIN_MOTIF_SUFFIX, trailing):
                m_type = GeneType.DOMAIN_MOTIF

            # Abbreviation Resolution
            if mention in paper.abb_sf_to_lf:
                long_form = paper.abb_sf_to_lf[mention]
                if long_form in mention_to_type:
                    m_type = mention_to_type[long_form]
                elif re.match(f'.*{_CELL_SUFFIX}', long_form):
                    m_type = GeneType.CELL
                elif re.match(f'.*{_FAMILY_NAME_SUFFIX}', long_form):
                    m_type = GeneType.FAMILY_NAME
                elif re.match(f'.*{_DOMAIN_MOTIF_SUFFIX}', long_form):
                    m_type = GeneType.DOMAIN_MOTIF

            mention_to_type[mention] = m_type
            passage.genes[i].type = m_type

            if m_type != GeneType.GENE:
                continue

            # Normalization pre-processing
            mention = annotation.text
            mtmp0 = re.match(PREPROCESS_PATTERN0, mention)
            mtmp1 = re.match(PREPROCESS_PATTERN1, mention)
            mtmp2 = re.match(PREPROCESS_PATTERN2, mention)
            mtmp3 = re.match(PREPROCESS_PATTERN3, mention)
            mtmp4 = re.match(PREPROCESS_PATTERN4, mention)
            mtmp5 = re.match(PREPROCESS_PATTERN5, mention)
            mtmp6 = re.match(PREPROCESS_PATTERN6, mention)
            mtmp7 = re.match(PREPROCESS_PATTERN7, mention)
            if mtmp0:
                mention += f'|{mtmp0.group(1)}'
            if mtmp1:
                mention += f'|{mtmp1.group(1)}'
            if mtmp2:
                mention += f'|{mtmp2.group(1)}a{mtmp2.group(2)}'
            if mtmp3:
                mention += f'|{mtmp3.group(1)}b{mtmp3.group(2)}'
            if mtmp4:
                mention += f'|{mtmp4.group(1)}alpha'
            if mtmp5:
                mention += f'|{mtmp5.group(1)}beta'
            if mtmp6:
                mention += f'|{mtmp6.group(1)}2{mtmp6.group(2)}'
            if mtmp7:
                mention += f'|{mtmp7.group(1)}3{mtmp7.group(2)}'
            passage.genes[i].text = mention

        # Recognize chromosomes
        locations = chromosome_tree.search_mention_location(passage.context)
        for location in locations:  # type: FoundMention
            ids = re.split('r[|,]', location.concept)
            for ID in ids:
                paper.chromosome_hash.add(ID)

    # Original implementation also has extension to all gene matches. We omit it, as it should be tagger's job.
