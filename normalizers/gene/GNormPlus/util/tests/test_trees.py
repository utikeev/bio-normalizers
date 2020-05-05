from normalizers.gene.GNormPlus.util.trees import PrefixTree, PrefixTranslation

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
    assert node is not None
    assert node.concept == '0'


def test_number_prefix_translation():
    tree = PrefixTree({})
    tree.insert('a-120', '0')
    node = tree.root.find_child('a')
    assert node is not None
    node = node.find_child('208', PrefixTranslation.NUMBER)
    assert node is not None
    assert node.concept == '0'
