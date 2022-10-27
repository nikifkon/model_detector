from dataclasses import dataclass
from functools import reduce

from algorithms.base import TokenBasedAlgorithm, NewSequenceResult
from algorithms.units_with_numbers import UnitExtractor
from algorithms.numbers_merge import NumbersMerge
from algorithms.units import UnitMerge
from algorithms.x_replace import XReplace
from algorithms.merge_soft import MergeSoft
from tokens import TokenSeq


def composite_function(*func):

    def compose(f, g):
        return lambda x: g(f(x))

    return reduce(compose, func, lambda x: x)


@dataclass(eq=True, frozen=True)
class DefaultResult(NewSequenceResult):
    pass


class DefaultAlgorithm(TokenBasedAlgorithm[DefaultResult]):
    def parse_by_tokens(self, seq: TokenSeq) -> DefaultResult:
        algorithm = composite_function(
            lambda seq: XReplace().parse_by_tokens(seq).seq,
            lambda seq: NumbersMerge().parse_by_tokens(seq).seq,
            lambda seq: MergeSoft().parse_by_tokens(seq).seq,
            lambda seq: UnitMerge().parse_by_tokens(seq).seq,
            lambda seq: UnitExtractor().parse_by_tokens(seq).seq,
        )  # TODO переписать так чтобы еще и замыканий не было
        return DefaultResult(None, algorithm(seq))
