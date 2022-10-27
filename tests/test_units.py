import pytest

from tokens import Sep, TokenSeq
from algorithms.units import Unit, UnitMerge, UnitExpression


@pytest.mark.parametrize('input, values', [
    ('Проволока стальная сварочная 4 мм Св-08ХН2ГМТА', ['мм']),
    ('test 220В', ['В']),
    ('Камера холодильная толщина 100 мм 4100х5600х2240 мм 42,96 м3 POLAIR', ['мм', 'мм', 'м^3']),
    ('(125кг на полку) ', ['кг', 'на']),
    ('Пилорама ленточная Алтай-3 (900) с бензиновым двигателем Lifan 15л.с.', ['л/с']),
    ('123 г2', []),
])
def test_simple_merge(input, values):
    um = UnitMerge()
    res = um.parse(input)
    assert list(token.value for token in res.seq.tokens if isinstance(token, UnitExpression)) == values


@pytest.mark.parametrize('unit, values, string', [
    (Unit('мм'), ('м', 'м', None), 'мм'),
    (Unit('м'), (None, 'м', None), 'м'),
    (Unit('м3'), (None, 'м', '^3'), 'м^3'),
    (Unit('л'), (None, 'л', None), 'л'),
    (Unit('кг'), ('к', 'г', None), 'кг'),
])
def test_unit_prefixes_suffixes(unit, values, string):
    assert unit.is_valid
    assert (unit.prefix, unit.norm, unit.suffix) == values
    assert str(unit) == string


@pytest.mark.parametrize('unit_exp, value', [
    (UnitExpression.from_seq(TokenSeq([Unit('л'), Sep('/'), Unit('с')])), 'л/с'),
    (UnitExpression.from_seq(TokenSeq([Unit('л'), Sep('.'), Unit('с'), Sep('.')])), 'л/с'),
    (UnitExpression.from_seq(TokenSeq([Unit('м^3'), Sep('/'), Unit('ч')])), 'м^3/ч')
])
def test_unit_expression(unit_exp, value):
    assert unit_exp.value == value
