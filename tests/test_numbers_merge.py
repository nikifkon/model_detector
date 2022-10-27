import pytest

from tokens import TokenSeq
from algorithms.numbers_merge import NumberMergeLog, NumbersMerge


@pytest.mark.parametrize('input, token_values', [
    ('Насос циркуляционный Stratos MAXO 65/0,5-9 PN6/10', ['Насос', 'циркуляционный', 'Stratos', 'MAXO', '65/0,5-9', 'PN', '6', '10']),
    ('Насос многоступенчатый Lowara 1SV12F007T/D 3×230/400 0.75 кВт 1', ['Насос', 'многоступенчатый', 'Lowara', '1', 'SV', '12', 'F', '007', 'T', 'D', '3×230/400', '0.75', 'кВт', '1']),
    ('1×1', ['1×1']),
    ('1-5', ['от 1 до 5']),
    ('1-5-6', ['1-5-6']),
    ('+1…+5', ['от +1 до +5']),
    ('12345 asdf', ['12345', 'asdf']),  # test no sep0 & not sep1
])
def test_numbers_merge(input: str, token_values: list[str]):
    seq = TokenSeq.from_string(input)
    res = NumbersMerge().parse_by_tokens(seq)
    assert list(map(lambda t: t.value, res.seq.iter_by_values())) == token_values


@pytest.mark.parametrize('input, token_values', [
    ('Проволока нержавеющая сварочная MIG ER-3210,8 мм', ['Проволока', 'нержавеющая', 'сварочная', 'MIG', 'ER', '3210', '8', 'мм']),
])
def test_dont_merge(input: str, token_values: list[str]):
    seq = TokenSeq.from_string(input)
    res = NumbersMerge().parse_by_tokens(seq)
    for token, expected_value in zip(res.seq.iter_by_values(), token_values):
        assert token.value == expected_value


@pytest.mark.parametrize('input, logs', [
    ('Насос циркуляционный Stratos MAXO 65/0,5-9 PN6/10', NumberMergeLog([' '], ['/', ',', '-'], [' '])),
    ('Насос многоступенчатый Lowara 1SV12F007T/D 3×230/400 0.75 кВт 1', NumberMergeLog([' ', ' '], ['×', '/', '.'], [' ', ' '])),
    ('Проволока нержавеющая сварочная MIG ER-3210,8 мм', NumberMergeLog())
])
def test_logs(input, logs):
    seq = TokenSeq.from_string(input)
    res = NumbersMerge().parse_by_tokens(seq)
    assert res.logs == logs
