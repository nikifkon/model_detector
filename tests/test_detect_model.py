import pytest

from algorithms.defaults import DefaultAlgorithm
from tokens import TokenSeq
from algorithms.detect_model import ModelDetector
from algorithms.find_manufacturer import ManufacturerToken


@pytest.mark.parametrize('input, model', [
    ('Насос циркуляционный MAXO 65/0,5-9 PN6/10', 'MAXO 65/0,5-9 PN6/10'),
    ('Подшипник универсальный NSK hr32307cn', 'NSK hr32307cn'),
    ('Газовая сварочная смесь К-25 смесь', 'К-25'),
    ('Подшипник универсальный', None),
    ('Компрессор DL-7.5/8-RF', 'DL-7.5/8-RF'),
    ('Шкаф холодильный Премьер АОДВЛЫ-2 (asd 1)', 'АОДВЛЫ-2'),  # first occurence has higher priority
    ('Проволока сварочная 6 мм, св08г2с, ГОСТ 2246-70', 'св08г2с'),
    ('Электроды ЦН-12М 4.5 мм', 'ЦН-12М'),
    ('Проволока титановая сварочная ОТ4-1св 6 мм ГОСТ 27265-87', 'ОТ4-1св'),
])
def test_without_manuf__simple(input: str, model: str):
    seq = DefaultAlgorithm().parse(input).seq

    res = ModelDetector(lambda x: False).parse_by_tokens(seq)
    if model is None:
        assert res.model is None
        return
    assert res.model is not None
    assert res.model.value == model


@pytest.mark.parametrize('input, manuf, model', [
    ('Подшипник ступицы Stellox 4030032SX', 'Stellox', '4030032SX'),
    ('Скважинный насос Pedrollo 4SR 1,5/46 - FK', 'Pedrollo', '4SR 1,5/46 - FK'),
    ('Подшипник универсальный NSK hr32307cn', 'NSK', 'hr32307cn'),
    ('Кронштейн Джамбо 50/28 до 2016 Джилекс', 'Джилекс', 'Джамбо 50/28'),
    ('Холодильный шкаф Wilo П-390С', 'Wilo', 'П-390С'),
    ('Ленточная пилорама Тайга Т4', 'Тайга', 'Т4'),
    ('Компрессор FUBAG SMART AIR, + 6 предметов', 'FUBAG', 'SMART AIR'),
    ('Льдогенератор чешуйчатого льда GASTRORAG DB ЕС65', 'GASTRORAG', 'DB ЕС65'),  # get last phrase

])
def test_with_manuf__simple(input: str, manuf: str, model: str):
    seq = DefaultAlgorithm().parse(input).seq
    with_manuf = []
    for token in seq.iter_by_tokens():
        if manuf == token.value:
            with_manuf.append(ManufacturerToken(token.value))
        else:
            with_manuf.append(token)
    seq = TokenSeq(with_manuf)

    res = ModelDetector(lambda x: False).parse_by_tokens(seq)
    assert res.model.value == model
