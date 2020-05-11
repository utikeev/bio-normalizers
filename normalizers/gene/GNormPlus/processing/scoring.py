import re
from typing import Dict, Set, Tuple

from normalizers.gene.GNormPlus.util.tokens import split_to_tokens


def score_function(gene_id: str, mention_hash: Set[str], long_form: str, scoring_hash: Dict[str, Tuple[str,int]],
                   scoring_df: Dict[str, float]) -> float:
    lf_tokens = split_to_tokens(long_form)
    lf_partial_match = 0

    match = re.match('[0-9]+-([0-9]+)', gene_id)
    if match:
        gene_id = 'Homo:' + match.group(1)
    else:
        gene_id = 'Gene:' + gene_id

    if gene_id in scoring_hash:
        token_freq: Dict[str, float] = {}
        term_freq: Dict[str, int] = {}

        scoring = scoring_hash[gene_id]
        tokens = scoring[0].split(',')
        for token in tokens:
            gene, freq = token.split('-')
            term_freq[gene] = int(freq)

        for mention in mention_hash:
            mention_tokens = split_to_tokens(mention)
            for token in mention_tokens:
                if token in term_freq:
                    token_freq[token] = term_freq[token]

        score = .0
        for token, freq in token_freq.items():
            for lf_token in lf_tokens:
                if lf_token == token:
                    lf_partial_match += 1

            tf_i_j = freq / scoring[1]
            id_fi = scoring_df[token]
            score += tf_i_j * id_fi * (1.0 / (1.0 - tf_i_j))

        if lf_partial_match > 0:
            score += lf_partial_match

        return score

    return .0
