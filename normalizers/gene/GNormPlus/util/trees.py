import re
from enum import Enum
from typing import Optional, Dict, List, NamedTuple

from normalizers.gene.GNormPlus.util.tokens import split_to_tokens


class PrefixTranslation(Enum):
    """Mode to find children in tree
    NONE — Simple lookup
    SUFFIX_TRANSLATION_MAP — Lookup in suffix translation
    NUMBER — If token is number, but not in the map take first found number token
    """
    NONE = 0
    SUFFIX_TRANSLATION_MAP = 1
    NUMBER = 2


class Node:
    """Tree node containing concept.

    Attributes:
        suffix_translation_map (Dict[str, str]):
            Suffices mapping between short and long forms.
        parent (:obj:`Node`, optional):
            Parent node.
        token (str):
            Token representing concept.
        concept (:obj:`str`, optional, defaults to :obj:`None`):
            Concept ID.
        children (Dict[str, Node]):
            Map from tokens to children.
    """

    def __init__(self, suffix_translation_map: Dict[str, str], parent: Optional['Node'], token: str, concept: Optional[str] = None):
        self.suffix_translation_map = suffix_translation_map
        self.parent = parent
        self.token = token
        self.concept = concept
        self.children: Dict[str, Node] = dict()

    def __str__(self):
        if self.concept:
            return f'{self.token}\t{self.concept}'
        else:
            return self.token

    def insert(self, token: str, concept: Optional[str] = None) -> 'Node':
        """Insert a new node under the target node.

        Args:
            token (str):
                Token representing new node.
            concept (:obj:`str`, optional, defaults to :obj:`None`):
                Concept ID.

        Returns:
            Inserted Node.
        """
        new_node = Node(self.suffix_translation_map, self, token, concept)
        self.children[token] = new_node
        return new_node

    def find_child(self, token: str, prefix_translation: PrefixTranslation = PrefixTranslation.NONE) -> Optional['Node']:
        """Find the child by token.

        Args:
            token (str):
                Token to look for.
            prefix_translation (:obj:`PrefixTranslation`, defaults to :obj:`PrefixTranslation.NONE`):
                Prefix translation mode.

        Returns:
            Child node if token was found, None otherwise.
        """
        if token in self.children:
            return self.children[token]

        if prefix_translation == PrefixTranslation.SUFFIX_TRANSLATION_MAP:
            if token in self.suffix_translation_map and self.suffix_translation_map[token] in self.children:
                return self.children[self.suffix_translation_map[token]]

        elif prefix_translation == PrefixTranslation.NUMBER and re.match(r'\d+', token):
            for entry in self.children.values():
                if re.match(r'\d+', entry.token):
                    return entry

        return None


ID_NOT_FOUND = '-1'
SUBSTRING_FOUND = '-2'
MENTION_NOT_FOUND = '-3'

_ROOT_NAME = '-ROOT-'


class FoundMention(NamedTuple):
    start: int
    end: int
    text: str
    concept: str


class PrefixTree:
    """Prefix tree of concepts.

    Attributes:
        suffix_translation_map (Dict[str, str]):
            Suffices mapping between short and long forms.
        root (Node):
            Root node of the tree.
    """

    def __init__(self, suffix_translation_map: Dict[str, str]):
        self.root = Node(suffix_translation_map, None, _ROOT_NAME)

    def insert(self, mention: str, concept: str) -> None:
        """Splits a mention into tokens and inserts them into the tree with given ids.

        Args:
            mention (str):
                Mention as is.
            concept (str):
                Its concept ID.
        """
        tokens = split_to_tokens(mention)
        tmp: Node = self.root
        for i, token in enumerate(tokens):
            child_node = tmp.find_child(token)
            if child_node:
                tmp = child_node
                if i == len(tokens) - 1:
                    tmp.concept = concept
            else:
                if i == len(tokens) - 1:
                    tmp = tmp.insert(token, concept)
                else:
                    tmp = tmp.insert(token)

    def pretty_print(self) -> str:
        """Recursively print the tree

        Returns:
            String representation of tree
        """
        return _pretty_print(self.root, '')

    def load_from_lines(self, lines: List[str]):
        """Loads prefix tree from lines

        Args:
            lines (List[str]):
                Sorted by location(!) lines in format [tree-location] [token] [conceptId?].
                Tree location should be separated with hyphens and all of the parts should be separated with tabulation.
        """
        last_depth = 0
        tmp: Node = self.root
        for line in lines:
            parts = line.strip().split('\t')
            locations = parts[0].split('-')
            token = parts[1]
            concept = parts[2] if len(parts) == 3 else ''
            while last_depth >= len(locations):
                last_depth -= 1
                tmp = tmp.parent
            last_depth = len(locations)
            tmp = tmp.insert(token, concept)

    def find_mention(self, mention: str) -> str:
        """Returns matching mention concept or one of the error concepts.

        Args:
            mention (str):
                Mention text.

        Returns:
            Concept of the mention or error code.
        """
        mentions = mention.split('|')
        for mention in mentions:
            tokens = split_to_tokens(mention)
            cnt = len(tokens)
            tmp: Optional[Node] = self.root
            found = -1
            prefix_translation = PrefixTranslation.NONE
            for i, token in enumerate(tokens):
                if i == cnt - 1:
                    prefix_translation = PrefixTranslation.SUFFIX_TRANSLATION_MAP
                tmp = tmp.find_child(token, prefix_translation)
                if tmp is None:
                    break
                found = i
            if found != -1:
                if found == cnt - 1:
                    if tmp.concept:
                        return tmp.concept
                    else:
                        return ID_NOT_FOUND
                else:
                    return SUBSTRING_FOUND

        return MENTION_NOT_FOUND

    def search_mention_location(self, context: str) -> List[FoundMention]:
        locations: List[FoundMention] = []
        lowered = context.lower()

        tokens = split_to_tokens(context)
        offset = 0
        start = 0
        last = 0
        first_time = 0
        for c in lowered:
            if not c.isspace():
                break
            offset += 1
        lowered.lstrip()
        i = 0
        while i < len(tokens):
            pre_i = i
            pre_start = start
            pre_last = last
            pre_lowered = lowered
            pre_offset = offset

            tmp = self.root
            found = False
            concept_found = i
            concept_found_mention: Optional[FoundMention] = None
            first_time_while = -1

            while True:
                token = tokens[i]
                child = tmp.find_child(token, PrefixTranslation.NUMBER)
                if child is None:
                    break
                tmp = child
                first_time_while += 1
                if start == 0 and first_time > 0:
                    start = offset
                if 0 < len(token) <= len(lowered) and lowered[0:len(token)] == token:
                    lowered = lowered[len(token):]
                    offset += len(token)

                last = offset
                for c in lowered:
                    if not c.isspace():
                        break
                    offset += 1
                lowered.lstrip()

                i += 1
                if tmp.concept and start < last < len(context):
                    concept_found = i
                    concept_found_mention = FoundMention(start, last, context[start:last], tmp.concept)
                found = True
                if i >= len(tokens):
                    break
                if first_time_while == 0:
                    pre_i = i
                    pre_start = start
                    pre_last = last
                    pre_lowered = lowered
                    pre_offset = offset

            if found:
                if tmp.concept and start < last < len(context):
                    locations.append(FoundMention(start, last, context[start:last], tmp.concept))
                else:
                    if concept_found_mention:
                        locations.append(concept_found_mention)
                        i = concept_found + 1
                    if first_time_while >= 1:
                        i = pre_i
                        lowered = pre_lowered
                        offset = pre_offset
                    start = 0
                    last = 0
                    if i > 0:
                        i -= 1
            else:
                if first_time_while >= 1 and tmp.concept is None:
                    i = pre_i
                    start = pre_start
                    last = pre_last
                    lowered = pre_lowered
                    offset = pre_offset

                    if 0 < len(token) <= len(lowered) and lowered[0:len(token)] == token:
                        lowered = lowered[len(token):]
                        offset += len(token)

            for c in lowered:
                if not c.isspace():
                    break
                offset += 1
            lowered.lstrip()
            first_time += 1

            i += 1

        return locations


def _pretty_print(node: Node, depth: str) -> str:
    res = ''
    if node.token != _ROOT_NAME:
        res += f'{depth}\t{node}\n'
    if depth != '':
        depth += '-'
    for i, child in enumerate(node.children.values()):
        res += _pretty_print(child, f'{depth}{i + 1}')
    return res
