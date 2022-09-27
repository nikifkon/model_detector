from algorithms.base import (BaseResult, TokenBasedAlgorithm)
from tokens import Token, TokenSeq


class Unit(Token):
    pass


class UnitExtractorResult(BaseResult):
    output: str
    units: dict[str, tuple[str, str]]


class UnitExtractor(TokenBasedAlgorithm[UnitExtractorResult]):
    break_symbol = "🎖️"

    def __init__(self):
        pass

    def parse_by_tokens(self, token_seq: TokenSeq) -> UnitExtractorResult:
        pass
        # iter throw token_seq
        #     if may be start for unit
        #     then run this thread with span
        #     and add to results
