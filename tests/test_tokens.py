import pytest

from algorithms.defaults import DefaultAlgorithm
from tokens import AsciiToken, TokenSeq


@pytest.mark.parametrize('input', [
    'Насос циркуляционный Stratos MAXO 65/0,5-9 PN6/10',
    'Ленточная пила для резки ПНД труб 1200 pro V2 400 В',
    'Насос многоступенчатый Lowara 1SV12F007T/D 3x230/400 0.75 кВт 1',
    'Компрессор винтовой FINI top 5008',
    'Коллектор ст. 11,8 мм, 5м., Ду 150мм, БРС Ду 150 (M+F) с упл. кольцом, с ш. кр, с БРС Ду 50 сф',
    'Насос для скважин Calpeda 4 SDF(M) 16, (Про-ть: Q max - 2,4 м3/ч )',
])
def test_tokenize_detokenize(input: str):
    assert str(TokenSeq.from_string(input)) == input


@pytest.mark.parametrize('input, token_values', [
    ('Ленточная пила для резки ПНД труб 1200 pro V2 400 В',
     ('Ленточная', 'пила', 'для', 'резки', 'ПНД', 'труб', '1200', 'pro', 'V', '2', '400', 'В')),
    ('Компрессор винтовой FINI top 5008', ('Компрессор', 'винтовой', 'FINI', 'top', '5008'))
])
def test_tokenize_simple(input: str, token_values: tuple[str]):
    seq = TokenSeq.from_string(input)
    for token, expected_value in zip(seq.iter_by_values(), token_values):
        assert token.value == expected_value


def test_simple_merge():
    seq = TokenSeq.from_string('1 2 3/4')
    seq2 = TokenSeq.from_string('1 2f 3 4')
    assert str(seq.merge([(1, 2)], lambda span: AsciiToken('A'))) == '1 A 3/4'
    assert str(seq.merge([(0, 2)], lambda span: AsciiToken('A'))) == 'A 3/4'
    assert str(seq.merge([(3, 4)], lambda span: AsciiToken('A'))) == '1 2 3/A'

    assert str(seq2.merge([(1, 3)], lambda span: AsciiToken('A'))) == '1 A 3 4'
    assert str(seq2.merge([(0, 2)], lambda span: AsciiToken('A'))) == 'Af 3 4'
    assert str(seq2.merge([(2, 3)], lambda span: AsciiToken('A'))) == '1 2A 3 4'


def test_multy_merge():
    seq = TokenSeq.from_string('1 2 3 4')
    assert str(seq.merge([(1, 2), (2, 3)], lambda span: AsciiToken('A'))) == '1 A A 4'


@pytest.mark.parametrize('input_string, start, end, expected_string', [
    ('1 2 3 4 5', 1, 3, '2 3'),
    ('1 2 3 4 5', 0, 3, '1 2 3'),
    ('1 2 3 4 5', 3, 5, '4 5'),
    ('1 2 3 4 5', 3, 5, '4 5'),
    ('1 2 3 4/5', 3, 5, '4/5'),
    ('1 2 3 4/5', 2, 4, '3 4'),  # controversial behavior
    ('1 2 3 4a', 2, 4, '3 4'),  # controversial behavior
])
def test_get_subseq(input_string: str, start: int, end: int, expected_string: str):
    seq = TokenSeq.from_string(input_string)
    res = seq.get_sub(start, end, index_by_values=True)
    assert str(res) == expected_string


@pytest.mark.parametrize('input_string, n, expected_strings', [
    ('1 2 3 4 5', 1, ['1', '2', '3', '4', '5']),
    ('1 2 3 4 5', 2, ['1 2', '2 3', '3 4', '4 5']),
    ('1 2 3 4 5', 3, ['1 2 3', '2 3 4', '3 4 5']),
    ('1 2 3-4 5;', 3, ['1 2 3-4', '2 3-4 5']),
    ('1 2 3TEST 5;', 3, ['1 2 3TEST', '2 3TEST 5']),
])
def test_iter_ngrams_simple(input_string, n, expected_strings):
    seq = DefaultAlgorithm().parse(input_string).seq
    assert list(map(lambda res: str(res[0]), seq.iter_ngrams_by_values(n))) == expected_strings


@pytest.mark.parametrize('input_string, expected_strings, predicate', [
    ('1 2 3 4 5', ['2 3'], lambda seq: seq.tokens[0].value == '2' and len(list(seq.iter_by_values())) <= 2),
    ('1 2 3-4 5', ['2 3-4'], lambda seq: seq.tokens[0].value == '2' and len(list(seq.iter_by_values())) <= 2),
])
def test_select_longest_ngrams_match(input_string, expected_strings, predicate):
    seq = DefaultAlgorithm().parse(input_string).seq
    assert list(map(lambda res: str(res[0]), seq.select_longest_ngrams_match(predicate))) == expected_strings


@pytest.mark.parametrize('input_string, expected_strings', [
    ('1 2 3 4 5 ', '1 2 3 4 5'),
    ('1 2 3;4 5;', '1 2 3;4 5'),
    (';1 2/3;4 5', ';1 2/3;4 5'),
])
def test_trim(input_string, expected_strings):
    seq = TokenSeq.from_string(input_string)
    assert str(seq.trim()) == expected_strings


@pytest.mark.parametrize('seq, expected_strings', [
    (TokenSeq.from_string('1 2 3 4 5'), '1;2;3;4;5'),
    (TokenSeq([AsciiToken('a-b')]), 'a;b'),
])
def test_dump_seq(seq, expected_strings):
    assert seq.dump_seq() == expected_strings
