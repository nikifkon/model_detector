import pytest

from algorithms.units import UnitExtractor


bs = UnitExtractor.break_symbol


@pytest.mark.parametrize('input, output, values', [
    ('Проволока стальная сварочная 4 мм Св-08ХН2ГМТА',
     f'Проволока стальная сварочная{bs}Св-08ХН2ГМТА',
     {('4', 'мм')}),
    ('Соединитель для шлангов от 10мм до 20мм',
     f'Соединитель для шлангов{bs}',
     {('10-20', 'мм')}),
    ('Камера холодильная толщина 100 мм 4100х5600х2240 мм 42,96 м3 POLAIR',
     f'Камера холодильная толщина{bs}POLAIR',
     {('100', 'мм'), ('4100×5600×2240', 'мм'), ('42,96', 'м3')}),
    ('Пилорама ленточная Алтай-3 (900) с бензиновым двигателем Lifan 15л.с.',
     f'Пилорама ленточная Алтай-3 (900) с бензиновым двигателем Lifan{bs}',
     {('15', 'л/с')})
])
def test_simple(input, output, values):
    ue = UnitExtractor()
    res = ue.parse(input)
    assert res.output == output
    assert set(res.units.values()) == values
