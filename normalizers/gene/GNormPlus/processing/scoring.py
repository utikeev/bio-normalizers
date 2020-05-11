import re
from typing import Dict, Set, Tuple

from normalizers.gene.GNormPlus.util.tokens import split_to_tokens


def score_function(gene_id: str, mention_hash: Set[str], long_form: str, scoring_hash: Dict[str, Tuple[str, int]],
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
        for token in tokens:  # type: str
            gene, freq = token.split('-')
            term_freq[gene] = int(freq)

        for mention in mention_hash:  # type: str
            mention_tokens = split_to_tokens(mention)
            for token in mention_tokens:  # type: str
                if token in term_freq:
                    token_freq[token] = term_freq[token]

        score = .0
        for token, freq in token_freq.items():  # type: str, float
            for lf_token in lf_tokens:  # type: str
                if lf_token == token:
                    lf_partial_match += 1

            if token in scoring_df:
                tf_i_j = freq / scoring[1]
                score += tf_i_j * scoring_df[token] * (1.0 / (1.0 - tf_i_j))

        if lf_partial_match > 0:
            score += lf_partial_match

        return score

    return .0
