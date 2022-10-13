from dataclasses import dataclass
from typing import Callable, Optional

from algorithms.base import TokenBasedAlgorithm, BaseResult
from connectors.models import ModelModel
from tokens import TokenSeq, ValueToken


class Model(ValueToken):
    pass


@dataclass
class FindModelsResult(BaseResult):
    model: Optional[ModelModel]


class FindModels(TokenBasedAlgorithm[FindModelsResult]):
    def __init__(self, is_model_exists: Callable[[TokenSeq], Optional[ModelModel]], is_prefix_exists=Callable[[TokenSeq], bool]):
        self.is_model_exists = is_model_exists
        if not is_prefix_exists:
            def is_prefix_exists():
                return True
        self.is_prefix_exists = is_prefix_exists

    def parse_by_tokens(self, token_seq: TokenSeq) -> FindModelsResult:
        res: list[tuple[TokenSeq, ModelModel]] = []
        # slow
        for n in range(2, len(list(token_seq.iter_by_values())) + 1):
            for ngram in token_seq.iter_ngrams_by_values(n):
                if model := self.is_model_exists(ngram):
                    res.append((ngram, model))
        if len(res) == 0:
            return FindModelsResult(None, None)
        if len(res) == 1:
            return FindModelsResult(None, res[0][1])
        assert False, (token_seq, res)
        # TODO условия на то что подстрока хорошая
