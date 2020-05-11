import re
from typing import Dict, Set, Optional, List, Tuple

from normalizers.gene.GNormPlus.models.paper import Paper, AnnotationType
from normalizers.gene.GNormPlus.processing.scoring import score_function
from normalizers.gene.GNormPlus.util.tokens import split_to_tokens
from normalizers.gene.GNormPlus.util.trees import PrefixTree

ID_KEY = 'ID'
TYPE_KEY = 'type'
GeneMentionHash = Dict[str, Dict[str, str]]
MentionHash = Set[str]
Filtering = Set[str]
GeneScoring = Dict[str, Tuple[str, int]]
GeneScoringDF = Dict[str, float]
GuaranteedGeneToID = Dict[str, str]
MultiGeneToId = Dict[str, str]


def fill_gene_mention_hash(paper: Paper, gene_mention_hash: GeneMentionHash, mention_hash: MentionHash, filtering: Filtering):
    for passage in paper.passages:
        for annotation in passage.annotations:
            start = annotation.location.start
            end = annotation.location.end
            mentions = annotation.text
            m_type = annotation.type
            tax_id = annotation.tax_id

            m_with_tax = f'{mentions}\t{tax_id}'

            # Filtering
            found_filter = False
            for item in filtering:
                if m_type == AnnotationType.GENE and re.match(f'.*{item}.*', mentions):
                    found_filter = True
                    break

            if not found_filter:
                if m_type == AnnotationType.GENE:
                    if m_with_tax in gene_mention_hash:
                        gene_mention_hash[m_with_tax][f'{start}\t{end}'] = ''
                    else:
                        gene_mention_hash[m_with_tax] = {f'{start}\t{end}': ''}
                        gene_mention_hash[m_with_tax][TYPE_KEY] = m_type.value
                        mention_hash.add(mentions)
                elif m_type == AnnotationType.FAMILY_NAME or m_type == AnnotationType.DOMAIN_MOTIF:
                    gms = mentions.split('|')
                    for g in gms:
                        mention_hash.add(g)


def find_in_gene_tree(paper: Paper, guaranteed_gene_to_id: GuaranteedGeneToID, multi_gene_to_id: MultiGeneToId, gene_tree: PrefixTree,
                      gene_mention_hash: GeneMentionHash):
    # Official name
    # Only one gene
    # Chromosome location
    for gene_mention_tax, hashes in gene_mention_hash.items():
        mentions, tax = gene_mention_tax.split('\t')
        gms = mentions.split('|')
        for mention in gms:
            id_str = gene_tree.find_mention(mention)
            ids = id_str.split('|')

            for ID in ids:
                tax_to_id = ID.split(':')  # taxID:geneIDs
                if tax_to_id[0] == tax:
                    hashes[ID_KEY] = tax_to_id[1]
                    break

            # Gene ID refinement
            if ID_KEY in hashes:
                gene_id = hashes[ID_KEY]
                match = re.match(r'\*([0-9]+(-[0-9]+))', gene_id)
                if match:  # Official name
                    hashes[ID_KEY] = match.group(1)
                    guaranteed_gene_to_id[gene_mention_tax] = match.group(1)
                elif re.match(r'[0-9]+(-[0-9]+)', gene_id):  # Only one gene
                    guaranteed_gene_to_id[gene_mention_tax] = gene_id
                else:  # Chromosome location
                    ids = gene_id.split(',')
                    found_by_chromosome = False
                    for ID in ids:
                        if ID in paper.chromosome_hash:
                            guaranteed_gene_to_id[gene_mention_tax] = ID
                            found_by_chromosome = True
                            break
                    if not found_by_chromosome:
                        multi_gene_to_id[gene_mention_tax] = gene_id


def infer_multiple_genes(guaranteed_gene_to_id: GuaranteedGeneToID, multi_gene_to_id: MultiGeneToId, gene_mention_hash: GeneMentionHash):
    # Multiple genes can be inferred by steps 1 and 2
    for multi_gene, ids_str in multi_gene_to_id.items():
        found_guaranteed = False
        for guaranteed_id in guaranteed_gene_to_id.values():
            ids = ids_str.split(',')
            for ID in ids:
                if ID == guaranteed_id:
                    gene_mention_hash[multi_gene][ID_KEY] = ID
                    found_guaranteed = True
                    break
            if found_guaranteed:
                break


def process_abbreviations(paper: Paper, gene_mention_hash: GeneMentionHash):
    # FullName -> Abbreviation
    # Abbreviation -> FullName
    for gene_mention_tax, hashes in gene_mention_hash.items():
        mentions, tax = gene_mention_tax.split('\t')
        other_form: Optional[str] = None
        if mentions.lower() in paper.abb_lf_to_sf:
            other_form = paper.abb_lf_to_sf[mentions] + '\t' + tax
        elif mentions.lower() in paper.abb_sf_to_lf:
            other_form = paper.abb_sf_to_lf[mentions] + '\t' + tax
        if other_form and other_form in gene_mention_hash and ID_KEY in hashes:
            gene_mention_hash[other_form][ID_KEY] = hashes[ID_KEY]


def rank_by_score_function(paper: Paper, gene_mention_hash: GeneMentionHash, mention_hash: MentionHash, gene_scoring: GeneScoring,
                           gene_scoring_df: GeneScoringDF):
    # Ranking by score function (inference network)
    for gene_mention_tax, hashes in gene_mention_hash.items():
        if ID_KEY in hashes and ',' in hashes[ID_KEY]:
            gene_ids: List[str] = hashes[ID_KEY].split(',')
            max_score = .0
            target_gene_id = ''
            for ID in gene_ids:
                mentions, tax = gene_mention_tax.split('\t')
                lf = ''
                if mentions.lower() in paper.abb_sf_to_lf:
                    lf = paper.abb_sf_to_lf[mentions]
                score = score_function(ID, mention_hash, lf, gene_scoring, gene_scoring_df)
                if score > max_score:
                    max_score = score
                    target_gene_id = ID
            hashes[ID_KEY] = target_gene_id


def remove_gmt(paper: Paper, gene_mention_hash: GeneMentionHash, gene_scoring: GeneScoring):
    # The inference network tokens of Abbreviation.ID should contain at least LF tokens
    # The short mention should be filtered if not long form support
    gmts: List[str] = []
    for gene_mention_tax, hashes in gene_mention_hash.items():
        mentions, tax = gene_mention_tax.split('\t')
        if TYPE_KEY in hashes and ID_KEY in hashes and hashes[TYPE_KEY] == AnnotationType.GENE.value:
            ID = hashes[ID_KEY]
            gene_id = ''
            match1 = re.match(r'^([0-9]+)-([0-9]+)$', ID)
            match2 = re.match(r'^([0-9]+)$', ID)
            if match1:
                gene_id = 'Homo:' + match1.group(2)
            elif match2:
                gene_id = 'Gene:' + match2.group(1)

            lf_token_match = False
            lf_exist = True
            if gene_id in gene_scoring:
                if mentions.lower() in paper.abb_sf_to_lf:
                    scoring = gene_scoring[gene_id]
                    tokens = scoring[0].split(',')
                    token_lexicon: List[str] = []
                    for token in tokens:
                        token_lexicon.append(token.split('-')[0])

                    lf_lower = paper.abb_sf_to_lf[mentions.lower()]
                    lf_tokens = split_to_tokens(lf_lower)
                    for word in token_lexicon:
                        for mention in lf_tokens:
                            if word == mention and not re.match('[0-9]+', mention):
                                lf_token_match = True
                else:
                    lf_exist = False
            else:
                lf_token_match = True

            if not lf_token_match and lf_exist:
                gmts.append(gene_mention_tax)
                gmts.append(paper.abb_sf_to_lf[mentions.lower()] + '\t' + tax)
            elif len(mentions) <= 2 and lf_exist:
                gmts.append(gene_mention_tax)

    for gmt in gmts:
        gene_mention_hash.pop(gmt)


def append_gene_ids(paper: Paper, gene_mention_hash: GeneMentionHash, family_name_tree: PrefixTree):
    # Append gene IDs
    gene_ids: Set[str] = set()
    for passage in paper.passages:
        for annotation in passage.annotations:
            if annotation.type == AnnotationType.GENE:
                m_with_tax = annotation.text + '\t' + annotation.tax_id
                if m_with_tax in gene_mention_hash and ID_KEY in gene_mention_hash[m_with_tax]:
                    gene_id = gene_mention_hash[m_with_tax][ID_KEY]
                    annotation.id = gene_id
                    gene_ids.add(gene_id.split('-')[0])

    # Extend to all gene mentions — omitted

    # FamilyName mentions to Genes
    for passage in paper.passages:
        for annotation in passage.annotations:
            if annotation.type == AnnotationType.FAMILY_NAME or annotation.type == AnnotationType.DOMAIN_MOTIF:
                ids = family_name_tree.find_mention(annotation.text)
                id_strs = ids.split('|')
                res: List[str] = []
                for ID in id_strs:
                    if ID in gene_ids:
                        res.append(ID)
                if len(res) != 0:
                    if annotation.type == AnnotationType.FAMILY_NAME:
                        annotation.type = AnnotationType.GENE
                    annotation.id = ';'.join(res)

    # Clean * and (anti)
    for passage in paper.passages:
        for annotation in passage.annotations:
            if annotation.type == AnnotationType.CELL:
                annotation.id.replace('*', '')
                annotation.id.replace('(anti)', '')
