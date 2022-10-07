import pytest

from tokens import TokenSeq
from algorithms.list_possible_sub_models import ListPossibleSubModels


@pytest.mark.parametrize('model, expected_list', [
    ('Stratos MAXO 65/0,5-9 PN6/10', ['Stratos MAXO 65/0,5-9 PN6', 'Stratos MAXO 65/0,5-9', 'Stratos MAXO 65']),
    ('АСО-ВК132/8-22', ['АСО-ВК132'])
])
def test_list_simple(model: str, expected_list: list[str]):
    seq = TokenSeq.from_string(model)
    res = ListPossibleSubModels().parse_by_tokens(seq)
    assert len(res.order_list) == len(expected_list)
    for seq, expected in zip(res.order_list, expected_list):
        assert str(seq) == expected


@pytest.mark.parametrize('model, expected_list', [
    ('234+', []),
])
def test_dont_list(model: str, expected_list: list[str]):
    seq = TokenSeq.from_string(model)
    res = ListPossibleSubModels().parse_by_tokens(seq)
    assert len(res.order_list) == len(expected_list)
    for seq, expected in zip(res.order_list, expected_list):
        assert str(seq) == expected
