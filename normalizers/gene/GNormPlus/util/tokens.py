import re
from typing import List


def split_to_tokens(mention: str) -> List[str]:
    mention = mention.lower()
    mention = re.sub(r'([0-9])([a-z])', r'\1 \2', mention)
    mention = re.sub(r'([a-z])([0-9])', r'\1 \2', mention)
    mention = re.sub(r'[\s\-_^;:,]+', ' ', mention)
    mention = re.sub(r'[ ]+', ' ', mention)
    return mention.split()
