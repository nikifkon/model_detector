import pytest

from algorithms.defaults import DefaultAlgorithm


@pytest.mark.parametrize('input, output', [
    ('Св3x3mm', 'Св3×3mm'),
])
def test_default(input: str, output: str):
    res = DefaultAlgorithm().parse(input)
    assert str(res.seq) == output
