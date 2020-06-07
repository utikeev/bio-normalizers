from bionorm.normalizers.gene.GNormPlus.util import PrefixTree, PrefixTranslation, ID_NOT_FOUND, SUBSTRING_FOUND, MENTION_NOT_FOUND

_SUFFIX_TRANSLATION_MAP = {
    'a': 'alpha',
    'alpha': 'a',
    'g': 'gamma',
    'y': 'gamma',
    'gamma': 'g',
}


def test_insert():
    tree = PrefixTree({})
    tree.insert('a-1', '0')
    tree.insert('a-2', '1')
    tree.insert('a-2_1', '2')
    tree.insert('bb', '5')

    expected = """1\ta
1-1\t1\t0
1-2\t2\t1
1-2-1\t1\t2
2\tbb\t5
"""
    assert tree.pretty_print() == expected


def test_suffix_translation_map():
    tree = PrefixTree(_SUFFIX_TRANSLATION_MAP)
    tree.insert('gamma', '0')
    node = tree.root.find_child('y', PrefixTranslation.SUFFIX_TRANSLATION_MAP)
    assert node
    assert node.concept == '0'


def test_number_prefix_translation():
    tree = PrefixTree({})
    tree.insert('a-120', '0')
    node = tree.root.find_child('a')
    assert node
    node = node.find_child('208', PrefixTranslation.NUMBER)
    assert node
    assert node.concept == '0'


def test_find_mention():
    tree = PrefixTree(_SUFFIX_TRANSLATION_MAP)
    tree.insert('a-1', '1')
    tree.insert('a-1-a', '2')

    concept = tree.find_mention('a-1-alpha')
    assert concept == '2'
    concept = tree.find_mention('a')
    assert concept == ID_NOT_FOUND
    concept = tree.find_mention('a-2')
    assert concept == SUBSTRING_FOUND
    concept = tree.find_mention('b')
    assert concept == MENTION_NOT_FOUND


def test_load_from_lines():
    tree = PrefixTree(_SUFFIX_TRANSLATION_MAP)
    lines_str = """1\ta
1-1\t1\t0
1-2\t2\t1
1-2-1\t1\t2
2\tbb\t5"""
    lines = lines_str.split('\n')
    tree.load_from_lines(lines)
    assert tree.pretty_print().strip() == lines_str
