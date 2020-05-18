from normalizers.disease.SieveBased.config.config import SieveBasedConfig
from normalizers.disease.SieveBased.processing.text_processor import TextProcessor

processor = TextProcessor.default()
processor.load_data()
nltk_processor = TextProcessor.nltk_stopword()
nltk_processor.load_data()


def test_stemming():
    initial = 'three grey geese on the green grass grazing grey were the geese and green was the grazing'
    expected = 'three grey gees on the green grass graze grey were the gees and green was the graze'
    assert expected == processor.get_stemmed_phrase(initial)


def test_correct_spelling():
    initial = 'this is the fist time it was done'
    expected = 'this is the first time it was done'
    assert expected == processor.correct_spelling(initial)


def test_get_string_preposition():
    string = 'first win in my life and of my career'
    assert 'in' == processor.get_preposition(string)
    string = 'no prepositions for you'
    assert processor.get_preposition(string) is None


def test_get_token_substring():
    tokens = ['leave', 'not', 'me', 'outside']
    assert 'not me' == processor.get_token_substring(tokens, 1, 3)


def test_get_suffix():
    assert 'sion' == processor.get_suffix('compulsion')


def test_get_prefix():
    assert 'three' == processor.get_prefix('three-legged')


def test_get_affix():
    assert 'cancer' == processor.get_affix('slow-cancer-induced')


def test_get_matching_tokens_count():
    string1 = "i am the string about giraffes but also cats"
    string2 = "And i am the string about giraffes but also dogs"
    # string, giraffes
    assert 2 == processor.get_matching_tokens_count(string1, string2)
    # string, giraffes, also
    assert 3 == nltk_processor.get_matching_tokens_count(string1, string2)
