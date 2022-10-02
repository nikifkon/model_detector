import pytest

from algorithms.numbers_merge import NumbersMerge
from algorithms.units import UnitMerge
from algorithms.units_with_numbers import UnitExtractor


@pytest.mark.parametrize('input, values', [
    ('Проволока стальная сварочная 4 мм Св-08ХН2ГМТА', {('4', 'мм')}),
    ('test 220В', {('220', 'В')}),
    ('Камера холодильная толщина 100 мм 4100×5600×2240 мм 42,96 м3 POLAIR', {('100', 'мм'), ('4100×5600×2240', 'мм'), ('42,96', 'м^3')}),
    ('(2500×1200×300 мм) (125кг на полку) ', {('2500×1200×300', 'мм'), ('125', 'кг')}),
    # ('Соединитель для шлангов от 10мм до 20мм', {('10-20', 'мм')}),  TODO expresions
    ('Пилорама ленточная Алтай-3 (900) с бензиновым двигателем Lifan 15л.с.', {('15', 'л/с')})
])
def test_simple(input, values):
    with_numbers = NumbersMerge().parse(input).seq
    with_units = UnitMerge().parse_by_tokens(with_numbers).seq
    ue = UnitExtractor()
    res = ue.parse_by_tokens(with_units)
    assert set(map(lambda x: (x.property_value.value, x.unit.value), res.units)) == values
