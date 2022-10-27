import pytest

from algorithms.merge_soft import MergeSoft
from algorithms.numbers_merge import NumbersMerge
from algorithms.units import UnitMerge
from algorithms.units_with_numbers import UnitExtractor, UnitProperty
from tokens import Sep, BreakToken, CyrillicToken, TokenSeq


def run_test(input: str, values: tuple):
    with_numbers = NumbersMerge().parse(input).seq
    with_merged = MergeSoft().parse_by_tokens(with_numbers).seq
    with_units = UnitMerge().parse_by_tokens(with_merged).seq
    res = UnitExtractor().parse_by_tokens(with_units)
    assert frozenset(map(lambda x: (x.property_value.value, x.unit.value), res.units)) == values


@pytest.mark.parametrize('input, output', [
    ('Проволока стальная сварочная 4 мм Св-08ХН2ГМТА', 'Проволока стальная сварочная 4 мм Св-08ХН2ГМТА'),
    ('test 220В', 'test 220 В'),
    ('Компрессор для пружин, 110-180мм / 400 мм KRAFTOOL', 'Компрессор для пружин, от 110 до 180 мм / 400 мм KRAFTOOL'),
    ('Парогенератор, 8-30', 'Парогенератор, 8-30'),
    ('Comprag DACS 10S', 'Comprag DACS 10S'),
    ('(на полку)', '(на полку)'),
    ('Компрессор Fest КМ 1800/50', 'Компрессор Fest КМ 1800/50'),
    ('Grundfos Hydro Multi-S/G 3 CM 50Hz', 'Grundfos Hydro Multi-S/G 3 CM 50 гц'),  # TODO см vs cm
])
def test_seq_with_units(input: str, output: str):
    with_numbers = NumbersMerge().parse(input).seq
    with_units = UnitMerge().parse_by_tokens(with_numbers).seq
    ue = UnitExtractor().parse_by_tokens(with_units)
    assert str(ue.seq) == output


@pytest.mark.parametrize('input, values', [
    ('Проволока стальная сварочная 4 мм Св-08ХН2ГМТА', frozenset([('4', 'мм')])),
    ('220В', frozenset([('220', 'В')])),
    ('Станок 2А5', frozenset()),
    ('Камера холодильная толщина 100 мм 4100×5600×2240 мм 42,96 м3 POLAIR',
     frozenset([('100', 'мм'), ('4100×5600×2240', 'мм'), ('42,96', 'м^3')])),
    ('(2500×1200×300 мм) (125кг на полку) ', frozenset([('2500×1200×300', 'мм'), ('125', 'кг')])),
    ('Пилорама ленточная Алтай-3 (900) с бензиновым двигателем Lifan 15л.с.', frozenset([('15', 'л/с')])),
    ('Компрессор воздушный 50 литров бу', frozenset([('50', 'л')])),
    ('Рукав напорно-всасывающий пвх 75мм, 8м', frozenset([('75', 'мм'), ('8', 'м')])),
    ('Электродвигатель 3 квт 950 об.мин', frozenset([('3', 'кВТ'), ('950', 'об/мин')])),
    ('Весы крановые 3 тонны', frozenset([('3', 'т')])),
    ('Новые холодильные камеры 200/400/220 см (15м3)', frozenset([('200/400/220', 'см'), ('15', 'м^3')])),
    ('Морской контейнер 20 футов б/у', frozenset([('20', 'фут')])),
    ('Рубительная машина ВХ600 24л/с, электростартер', frozenset([('24', 'л/с')])),
    ('Винтовой компрессор ABAC SPINN 5.5X FM - 8 бар', frozenset([('8', 'бар')])),
    ('Мотопомпы 433 л.мин', frozenset([('433', 'л/мин')])),
    ('02. 224P 3000 Тележка инструментальная открытая с2 полками', frozenset()),
    ('Двигатель BMH 3.4НМ', frozenset([('3.4', 'нм')])),
])
def test_basic(input, values):
    run_test(input, values)


@pytest.mark.parametrize('input, values', [
    ('Подшипник ООО ГПЗ 80- 32317 М', frozenset([])),
    ('Подшипник MPZ 170314 Л', frozenset([])),
    ('Подшипник апп 8222 км', frozenset([]))
])
def test_limit(input, values):
    run_test(input, values)


@pytest.mark.parametrize('input, seq', [
    ('Мотопомпы метр фыва', TokenSeq(
        [CyrillicToken('Мотопомпы'), Sep(' '), CyrillicToken('метр'), Sep(' '), CyrillicToken('фыва'), BreakToken()])),
])
def test_no_unit_tokens_if_no_numbers(input: str, seq: TokenSeq):
    with_numbers = NumbersMerge().parse(input).seq
    with_units = UnitMerge().parse_by_tokens(with_numbers).seq
    res = UnitExtractor().parse_by_tokens(with_units)
    assert res.seq == seq


@pytest.mark.parametrize('input, values', [
    # ('Силиконовая резина 1,0мм х 1000мм', frozenset([('1×1000', 'мм')])),
    # ("Соединитель для шлангов от 10мм до 20мм", frozenset([('от 10 до 20', 'мм')])),
    # ('Витрина холодильная настольная ВХН-70-01, +5…+15 С', frozenset([('от +5 до +15', 'с')])),
    # ('Компрессор для пружин, 110-180мм / 400 мм KRAFTOOL', frozenset([('от 110 до 180', 'мм'), ('400', 'мм')])),
    # ('Холодильный шкаф Капри П-390С', frozenset()),
    ('Сушильный комплекс для древесины на 40 куб.м', frozenset([('40', 'м^3')])),
    ('Термопенал КЕДР П- 5 (220 В, 150 °C, загрузка 5 кг)', frozenset([('220', 'В'), ('150', '°C'), ('5', 'кг')]))
])
def test_advanced(input: str, values: set[tuple[str, str]]):
    run_test(input, values)


def run_with_property_names(input: str, data: dict):
    with_numbers = NumbersMerge().parse(input).seq
    with_merged = MergeSoft().parse_by_tokens(with_numbers).seq
    with_units = UnitMerge().parse_by_tokens(with_merged).seq
    res = UnitExtractor().parse_by_tokens(with_units)
    assert UnitProperty.to_dict(res.units) == data


@pytest.mark.parametrize('input,data', [
    ('Ультракомпактный фильтр FL 160мм', {'Размер': ('160', 'мм')}),
    ('Ультракомпактный фильтр FL d 160мм', {'Диаметр': ('160', 'мм')}),
    ('Ультракомпактный фильтр FL d=160мм', {'Диаметр': ('160', 'мм')}),
    ('Ультракомпактный фильтр FL d.160мм', {'Диаметр': ('160', 'мм')}),
])
def test_with_properties_name__simple(input: str, data: dict):
    run_with_property_names(input, data)


@pytest.mark.parametrize('input,data', [
    ('Вкладыши шатуна ВК-108-02 Р2 d-99,0 мм на компрессор 2ВМ2,5-14/9', {'Диаметр': ('99', 'мм')}),
    ('Пруток сварочный ALSI 5, D= 2 мм.', {'Диаметр': ('2', 'мм')}),
    ('Переводник переходный НКТ 60х33 ГОСТ 23979-80 L=170 мм', {'Длина': ('170', 'мм')}),
    ('Сменная насадка VOLL для аппарата раструбной сварки, V-Weld, диаметр 32 мм', {'Диаметр': ('32', 'мм')}),
    ('Шнек для мотобура Carver GDB - 250/2, двухзаходный, для грунта, 250мм, L= 800мм, диаметр соединения 20мм (01. 003. 00051)',
        {'Длина': ('800', 'мм'), 'Диаметр соединения': ('20', 'мм')}),
    ('Форма-резак Цифра Три 25 см., высота 5 см.', {'Высота': ('5', 'см'), 'Размер': ('25', 'см')}),
    ('Станок заточный (точило) ЗУБР СТ - 200, 400Вт, 2950 об/мин, диаметр круга 200мм, толщина круга 20мм, для заточки инструмента и ножей',
        {'Мощность': ('400', 'ВТ'), 'Диаметр круга': ('200', 'мм'), 'Толщина круга': ('20', 'мм')}),
])
def test_with_properties_name__advanced(input: str, data: dict):
    run_with_property_names(input, data)

# TODO test with properties
# Станок заточный (точило) ЗУБР СТ - 200, 400Вт, 2950 об/мин, диаметр круга 200мм, толщина круга 20мм, для заточки инструмента и ножей
# Форма-резак Цифра Три 25 см., высота 5 см.
# Шнек для мотобура Carver GDB - 250/2, двухзаходный, для грунта, 250мм, L= 800мм, диаметр соединения 20мм (01. 003. 00051)
# Сменная насадка VOLL для аппарата раструбной сварки, V-Weld, диаметр 32 мм
# Переводник переходный НКТ 60х33 ГОСТ 23979-80 L=170 мм
# Пруток сварочный ALSI 5, D= 2 мм.
# Вкладыши шатуна ВК-108-02 Р2 d-99,0 мм на компрессор 2ВМ2,5-14/9
# б/у
# Штабелер подъемник ручной механический б/у
# Столярные станки бу

# ГОСТ
# Страна
# №5
