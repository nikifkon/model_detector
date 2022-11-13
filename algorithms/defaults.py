from dataclasses import dataclass
from functools import reduce

from algorithms.base import TokenBasedAlgorithm, NewSequenceResult
from algorithms.units_with_numbers import UnitExtractor, UnitProperty
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
    properties: dict[str, tuple[str, str]]
    # TODO get results


class DefaultAlgorithm(TokenBasedAlgorithm[DefaultResult]):
    def parse_by_tokens(self, seq: TokenSeq) -> DefaultResult:
        properties: dict[str, tuple[str, str]] = {}

        def property_alg(seq: TokenSeq):
            nonlocal properties
            res = UnitExtractor().parse_by_tokens(seq)
            properties = UnitProperty.to_dict(res.units)
            return res.seq

        algorithm = composite_function(
            lambda seq: XReplace().parse_by_tokens(seq).seq,
            lambda seq: NumbersMerge().parse_by_tokens(seq).seq,
            lambda seq: UnitMerge().parse_by_tokens(seq).seq,
            property_alg,
            lambda seq: MergeSoft().parse_by_tokens(seq).seq,
        )
        return DefaultResult(algorithm(seq), properties)
