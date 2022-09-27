import pytest

from tokens import TokenSeq


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
    ('Ленточная пила для резки ПНД труб 1200 pro V2 400 В', ['Ленточная', 'пила', 'для', 'резки', 'ПНД', 'труб', '1200', 'pro', 'V', '2', '400', 'В']),
    ('Компрессор винтовой FINI top 5008', ['Компрессор', 'винтовой', 'FINI', 'top', '5008'])
])
def test_tokenize_simple(input: str, token_values: list[str]):
    seq = TokenSeq.from_string(input)
    for token, expected_value in zip(seq.tokens, token_values):
        assert token.value == expected_value
