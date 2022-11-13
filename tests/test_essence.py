import pytest

from algorithms.detect_essence import EssenceFinder


@pytest.mark.parametrize('product_name, essence', [
    ('Насос циркуляционный', 'Насос'),
    ('Проволока нержавеющая сварочная', 'Проволока'),
    ('Листогиб с поворотной балкой', 'Листогиб'),
    (None, None),
])
def test_numbers_merge(connector, product_name: str, essence: str):
    res = EssenceFinder(connector.check_is_essence_banned).parse(product_name)
    assert res.essence == essence
