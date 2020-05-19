import re
from typing import Dict, Set, Optional, List, Tuple, Pattern

from normalizers.gene.GNormPlus.models.paper import GNormPaper, GeneType, Passage, GNormGeneMention, GNormSpeciesAnnotation, \
    SpeciesAnnotationPlacement
from normalizers.gene.GNormPlus.processing.scoring import score_function
from normalizers.gene.GNormPlus.processing.species import HUMAN_ID
from normalizers.gene.GNormPlus.util.re_patterns import SINGLE_GENE_PATTERN, MULTI_GENE_PATTERN, GENE_GMT_PATTERN, HOMO_GMT_PATTERN, \
    NUMBER_PATTERN
from normalizers.gene.GNormPlus.util.tokens import split_to_tokens
from normalizers.gene.GNormPlus.util.trees import PrefixTree

ID_KEY = 'ID'
TYPE_KEY = 'type'
FALLBACK_KEY = 'fallback'
GeneMentionHash = Dict[str, Dict[str, str]]
MentionHash = Set[str]
Filtering = Set[Pattern[str]]
GeneScoring = Dict[str, Tuple[str, int]]
GeneScoringDF = Dict[str, float]
GuaranteedGeneToID = Dict[str, str]
MultiGeneToId = Dict[str, str]


def fill_gene_mention_hash(paper: GNormPaper, gene_mention_hash: GeneMentionHash, mention_hash: MentionHash, filtering: Filtering):
    for passage in paper.passages:  # type: Passage
        for gene in passage.genes:  # type: GNormGeneMention
            gene: GNormGeneMention
            start = gene.location.start
            end = gene.location.end
            mentions = gene.text
            m_type = gene.type
            tax_id = gene.tax_id.id

            m_with_tax = f'{mentions}\t{tax_id}'

            # Filtering [Disabled]
            found_filter = False
            # for item in filtering:  # type: Pattern[str]
            #     if m_type == GeneType.GENE and re.match(item, mentions):
            #         found_filter = True
            #         break

            if not found_filter:
                if m_type == GeneType.GENE:
                    if m_with_tax in gene_mention_hash:
                        gene_mention_hash[m_with_tax][f'{start}\t{end}'] = ''
                    else:
                        gene_mention_hash[m_with_tax] = {f'{start}\t{end}': ''}
                        gene_mention_hash[m_with_tax][TYPE_KEY] = m_type.value
                        mention_hash.add(mentions)
                elif m_type == GeneType.FAMILY_NAME or m_type == GeneType.DOMAIN_MOTIF:
                    gms = mentions.split('|')
                    for g in gms:
                        mention_hash.add(g)


def find_in_gene_tree(paper: GNormPaper, guaranteed_gene_to_id: GuaranteedGeneToID, multi_gene_to_id: MultiGeneToId, gene_tree: PrefixTree,
                      gene_mention_hash: GeneMentionHash):
    # Official name
    # Only one gene
    # Chromosome location
    for gene_mention_tax, hashes in gene_mention_hash.items():  # type: str, Dict[str, str]
        mentions, tax = gene_mention_tax.split('\t')  # type: str, str
        gms = mentions.split('|')
        for mention in gms:  # type: str
            id_str = gene_tree.find_mention(mention)
            ids = id_str.split('|')

            for ID in ids:  # type: str
                tax_to_id = ID.split(':')  # taxID:geneIDs
                if tax_to_id[0] == tax:
                    hashes[ID_KEY] = tax_to_id[1]
                    break

            if tax != HUMAN_ID and ID_KEY not in hashes:
                for ID in ids:  # type: str
                    tax_to_id = ID.split(':')
                    if tax_to_id[0] == HUMAN_ID:
                        hashes[ID_KEY] = tax_to_id[1]
                        hashes[FALLBACK_KEY] = HUMAN_ID
                        break

            # Gene ID refinement
            if ID_KEY in hashes:
                gene_id = hashes[ID_KEY]
                match = re.match(MULTI_GENE_PATTERN, gene_id)
                if match:  # Official name
                    hashes[ID_KEY] = match.group(1)
                    guaranteed_gene_to_id[gene_mention_tax] = match.group(1)
                elif re.match(SINGLE_GENE_PATTERN, gene_id):  # Only one gene
                    guaranteed_gene_to_id[gene_mention_tax] = gene_id
                else:  # Chromosome location
                    ids = gene_id.split(',')
                    found_by_chromosome = False
                    for ID in ids:  # type: str
                        if ID in paper.chromosome_hash:
                            guaranteed_gene_to_id[gene_mention_tax] = ID
                            found_by_chromosome = True
                            break
                    if not found_by_chromosome:
                        multi_gene_to_id[gene_mention_tax] = gene_id


def infer_multiple_genes(guaranteed_gene_to_id: GuaranteedGeneToID, multi_gene_to_id: MultiGeneToId, gene_mention_hash: GeneMentionHash):
    # Multiple genes can be inferred by steps 1 and 2
    for multi_gene, ids_str in multi_gene_to_id.items():  # type: str, str
        found_guaranteed = False
        for guaranteed_id in guaranteed_gene_to_id.values():  # type: str
            ids = ids_str.split(',')
            for ID in ids:  # type: str
                if ID == guaranteed_id:
                    gene_mention_hash[multi_gene][ID_KEY] = ID
                    found_guaranteed = True
                    break
            if found_guaranteed:
                break


def process_abbreviations(paper: GNormPaper, gene_mention_hash: GeneMentionHash):
    # FullName -> Abbreviation
    # Abbreviation -> FullName
    for gene_mention_tax, hashes in gene_mention_hash.items():  # type: str, Dict[str, str]
        mentions, tax = gene_mention_tax.split('\t')  # type: str, str
        other_form: Optional[str] = None
        lowered_mention = mentions.lower()
        if lowered_mention in paper.abb_lf_to_sf:
            other_form = paper.abb_lf_to_sf[lowered_mention] + '\t' + tax
        elif lowered_mention in paper.abb_sf_to_lf:
            other_form = paper.abb_sf_to_lf[lowered_mention] + '\t' + tax
        if other_form and other_form in gene_mention_hash and ID_KEY in hashes:
            gene_mention_hash[other_form][ID_KEY] = hashes[ID_KEY]


def rank_by_score_function(paper: GNormPaper, gene_mention_hash: GeneMentionHash, mention_hash: MentionHash, gene_scoring: GeneScoring,
                           gene_scoring_df: GeneScoringDF):
    # Ranking by score function (inference network)
    for gene_mention_tax, hashes in gene_mention_hash.items():  # type: str, Dict[str, str]
        if ID_KEY in hashes and ',' in hashes[ID_KEY]:
            gene_ids: List[str] = hashes[ID_KEY].split(',')
            max_score = .0
            target_gene_id = ''
            for ID in gene_ids:
                mentions, tax = gene_mention_tax.split('\t')
                lowered_mention = mentions.lower()
                if lowered_mention in paper.abb_sf_to_lf:
                    lf = paper.abb_sf_to_lf[lowered_mention]
                    score = score_function(ID, mention_hash, lf, gene_scoring, gene_scoring_df)
                    if score > max_score:
                        max_score = score
                        target_gene_id = ID
            hashes[ID_KEY] = target_gene_id


def remove_gmt(paper: GNormPaper, gene_mention_hash: GeneMentionHash, gene_scoring: GeneScoring):
    # The inference network tokens of Abbreviation.ID should contain at least LF tokens
    # The short mention should be filtered if not long form support
    gmts: List[str] = []
    for gene_mention_tax, hashes in gene_mention_hash.items():  # type: str, Dict[str, str]
        mentions, tax = gene_mention_tax.split('\t')  # type: str, str
        if TYPE_KEY in hashes and ID_KEY in hashes and hashes[TYPE_KEY] == GeneType.GENE.value:
            ID = hashes[ID_KEY]
            gene_id = ''
            match1 = re.match(HOMO_GMT_PATTERN, ID)
            match2 = re.match(GENE_GMT_PATTERN, ID)
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
                    for token in tokens:  # type: str
                        token_lexicon.append(token.split('-')[0])

                    lf_lower = paper.abb_sf_to_lf[mentions.lower()]
                    lf_tokens = split_to_tokens(lf_lower)
                    for word in token_lexicon:  # type: str
                        for mention in lf_tokens:  # type: str
                            if word == mention and not re.match(NUMBER_PATTERN, mention):
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

    for gmt in gmts:  # type: str
        gene_mention_hash.pop(gmt, None)


def append_gene_ids(paper: GNormPaper, gene_mention_hash: GeneMentionHash, family_name_tree: PrefixTree):
    # Append gene IDs
    gene_ids: Set[str] = set()
    for passage in paper.passages:  # type: Passage
        for gene in passage.genes:  # type: GNormGeneMention
            if gene.type == GeneType.GENE:
                m_with_tax = gene.text + '\t' + gene.tax_id.id
                if m_with_tax in gene_mention_hash and ID_KEY in gene_mention_hash[m_with_tax]:
                    gene_id = gene_mention_hash[m_with_tax][ID_KEY]
                    gene.id = gene_id
                    if FALLBACK_KEY in gene_mention_hash[m_with_tax]:
                        gene.tax_id = GNormSpeciesAnnotation(gene_mention_hash[m_with_tax][FALLBACK_KEY],
                                                             SpeciesAnnotationPlacement.FALLBACK)
                    gene_ids.add(gene_id.split('-')[0])
            elif gene.type == GeneType.FAMILY_NAME or gene.type == GeneType.DOMAIN_MOTIF:
                ids = family_name_tree.find_mention(gene.text)
                id_strs = ids.split('|')
                res: List[str] = []
                for ID in id_strs:  # type: str
                    if ID in gene_ids:
                        res.append(ID)
                if len(res) != 0:
                    if gene.type == GeneType.FAMILY_NAME:
                        gene.type = GeneType.GENE
                    gene.id = ';'.join(res)
            elif gene.type == GeneType.CELL and gene.id:
                gene.id.replace('*', '')
                gene.id.replace('(anti)', '')
