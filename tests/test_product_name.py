import pytest

from algorithms.defaults import DefaultAlgorithm
from algorithms.detect_product_name import ProductNameFinder
from tests.conftest import MockConnector


@pytest.mark.parametrize('input, product_name', [
    ('Насос циркуляционный Stratos MAXO 65/0,5-9 PN6/10', 'Насос циркуляционный'),
    ('Проволока нержавеющая сварочная MIG ER-3210,8 мм', 'Проволока нержавеющая сварочная'),
    ('305мм х 500м, 32мкм, 76мм', None),
    ('Мотопомпы 433', 'Мотопомпы'),
    ('Пленка для ламинирования рулонная Без бренда 305мм х 500м, 32мкм, 76мм глянец', 'Пленка для ламинирования рулонная'),
    ('Электромеханический зиговочный станок IKMN', 'Электромеханический зиговочный станок'),
    ('Насос центробежный консольно-моноблочный NB', 'Насос центробежный консольно-моноблочный'),
])
def test_product_name_simple(input: str, product_name: str):
    seq = DefaultAlgorithm().parse(input).seq
    res = ProductNameFinder(MockConnector().check_is_essence_banned).parse_by_tokens(seq)
    if product_name is None:
        assert res.product_name is None
        return
    assert res.product_name is not None
    assert res.product_name.value == product_name
