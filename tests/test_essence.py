import pytest

from algorithms.detect_essence import EssenceFinder
from algorithms.detect_product_name import ProductNameToken
from tests.conftest import MockConnector


@pytest.mark.parametrize('product_name, essence', [
    (ProductNameToken('Насос циркуляционный'), 'Насос'),
    (ProductNameToken('Проволока нержавеющая сварочная'), 'Проволока'),
    (None, None),
])
def test_numbers_merge(product_name: ProductNameToken, essence: str):
    res = EssenceFinder(MockConnector().check_is_essence_banned).parse(product_name)
    assert res.essence == essence
