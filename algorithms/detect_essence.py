from dataclasses import dataclass
from typing import Callable

from algorithms.base import BaseAlgorithm, BaseResult, BaseSelector
from data.essence import can_be_essence
from tokens import TokenSeq


@dataclass(eq=True, frozen=True)
class EssenceFinderResult(BaseResult):
    essence: str


class EssenceFinder(BaseAlgorithm[EssenceFinderResult]):
    def __init__(self, is_banned: Callable[[TokenSeq], bool]):
        self.is_banned = is_banned

    def parse(self, product_name: str) -> EssenceFinderResult:
        res = []
        if product_name:
            for context, token in TokenSeq.from_string(product_name).iter_with_context():
                if can_be_essence(context, token):
                    res.append(EssenceFinderResult(token.value.capitalize()))
        return SelectEssence().select(res)


class SelectEssence(BaseSelector[EssenceFinderResult]):
    def select(self, input: list[EssenceFinderResult]) -> EssenceFinderResult:
        return input[0] if input else EssenceFinderResult(None)
