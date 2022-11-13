import pytest

from algorithms.merge_soft import MergeSoft, MergedToken
from tokens import TokenSeq, DigitToken, Sep


@pytest.mark.parametrize('input, output', [
    ('1 2 3 4', TokenSeq.from_string('1 2 3 4')),
    ('1 2 3-4', TokenSeq([DigitToken('1'), Sep(' '), DigitToken('2'), Sep(' '), MergedToken('3-4')])),
    ('1 2 3a', TokenSeq([DigitToken('1'), Sep(' '), DigitToken('2'), Sep(' '), MergedToken('3a')])),
])
def test_merge_soft_simple(input: str, output: str):
    res = MergeSoft().parse(input)
    assert res.seq == output
