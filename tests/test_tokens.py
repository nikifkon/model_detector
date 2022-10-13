import pytest

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
    ('Ленточная пила для резки ПНД труб 1200 pro V2 400 В', ('Ленточная', 'пила', 'для', 'резки', 'ПНД', 'труб', '1200', 'pro', 'V', '2', '400', 'В')),
    ('Компрессор винтовой FINI top 5008', ('Компрессор', 'винтовой', 'FINI', 'top', '5008'))
])
def test_tokenize_simple(input: str, token_values: tuple[str]):
    seq = TokenSeq.from_string(input)
    for token, expected_value in zip(seq.iter_by_values(), token_values):
        assert token.value == expected_value


def test_simple_merge():
    seq = TokenSeq.from_string('1 2 3 4')
    seq2 = TokenSeq.from_string('1 2f 3 4')
    assert str(seq.merge([(1, 2)], lambda span: AsciiToken('A'))) == '1 A 3 4'
    assert str(seq.merge([(0, 2)], lambda span: AsciiToken('A'))) == 'A 3 4'
    assert str(seq.merge([(3, 4)], lambda span: AsciiToken('A'))) == '1 2 3 A'
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
])
def test_get_subseq(input_string: str, start: int, end: int, expected_string: str):
    seq = TokenSeq.from_string(input_string)
    res = seq.get_sub(start, end, index_by_values=True)
    assert str(res) == expected_string


@pytest.mark.parametrize('input_string, n, expected_strings', [
    ('1 2 3 4 5', 1, ['1', '2', '3', '4', '5']),
    ('1 2 3 4 5', 2, ['1 2', '2 3', '3 4', '4 5']),
    ('1 2 3 4 5', 3, ['1 2 3', '2 3 4', '3 4 5']),
    ('1 2 3;4 5;', 3, ['1 2 3', '2 3;4', '3;4 5']),
])
def test_iter_ngrams_simple(input_string, n, expected_strings):
    seq = TokenSeq.from_string(input_string)
    assert list(map(str, seq.iter_ngrams_by_values(n))) == expected_strings
