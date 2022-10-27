from dataclasses import dataclass
from typing import Callable, Optional

from algorithms.base import NewSequenceResult, TokenBasedAlgorithm
from connectors.models import SeriesModel
from tokens import TokenSeq, ValueToken, SereisToken


class SeriesToken(ValueToken):
    pass


@dataclass(eq=True, frozen=True)
class FindSeriesResult(NewSequenceResult):
    series: Optional[SeriesModel]


class FindSeries(TokenBasedAlgorithm[FindSeriesResult]):
    def __init__(self, is_series_exists: Callable[[TokenSeq], Optional[SeriesModel]]):
        self.is_series_exists = is_series_exists

    def parse_by_tokens(self, token_seq: TokenSeq) -> FindSeriesResult:
        res: list[tuple[tuple[int, int], SeriesModel]] = []
        # slow
        for n in range(1, len(list(token_seq.iter_by_values())) + 1):
            for ngram, start, end in token_seq.iter_ngrams_by_values(n):
                if series := self.is_series_exists(ngram):
                    res.append(((start, end), series))
        if len(res) == 0:
            return FindSeriesResult(None, seq=token_seq, series=None)
        if len(res) == 1:
            return FindSeriesResult(None,
                                    seq=token_seq.merge([res[0][0]], lambda x: SereisToken(res[0][1])),
                                    series=res[0][1])
        print(token_seq)
        return FindSeriesResult(None,
                                seq=token_seq.merge([res[0][0]], lambda x: SereisToken(res[0][1])),
                                series=res[0][1])
        # TODO условия на то что подстрока хорошая
