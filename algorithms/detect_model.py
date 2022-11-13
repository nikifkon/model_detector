from dataclasses import dataclass
from typing import Callable

from algorithms.base import NewSequenceResult, TokenBasedAlgorithm, BaseSelector
from algorithms.merge_soft import MergedToken
from data.dictionary import is_token_in_cyrillic_dictionary
from tokens import AsciiToken, BreakToken, Context, DigitToken, TokenSeq, ModelToken, Token, DataToken, Sep, \
    CyrillicToken


@dataclass(eq=True, frozen=True)
class ModelDetectorResult(NewSequenceResult):
    model: ModelToken
    score: int


class ModelDetector(TokenBasedAlgorithm[ModelDetectorResult]):
    breaking_seps = {'(', ')', ';', '[', ']', ','}
    soft_seps = {'-'}

    def __init__(self, is_banned: Callable[[TokenSeq], bool]):
        self.is_banned = is_banned

    def start_condition(self, token: Token):
        if isinstance(token, Sep):
            return False
        return True

    def continue_condition(self, token: Token, context: Context, cur_score: int) -> tuple[bool, int]:
        if isinstance(token, (BreakToken, DataToken)):
            return False, 0
        if isinstance(token, Sep):
            return not any(c in self.breaking_seps for c in set(token.value)), 0
        if is_token_in_cyrillic_dictionary(context, token):
            return False, 0
        if isinstance(token, (AsciiToken, DigitToken, MergedToken)):
            return True, +6
        if isinstance(token, (CyrillicToken,)):
            return True, +3
        return False, 0

    def parse_by_tokens(self, token_seq: TokenSeq) -> ModelDetectorResult:
        res: list[ModelDetectorResult] = []
        gen = token_seq.generate_with_context()
        score = 0
        for context, token in gen:
            chunk_start = context.value_index
            if self.start_condition(token):
                while True:
                    to_cont, score_delta = self.continue_condition(token, context, score)
                    score += score_delta
                    if not to_cont:
                        break
                    context, token = gen.send(+1)
                chunk_end = context.value_index + isinstance(token, (BreakToken, Sep))
                if chunk_end - chunk_start <= 0:
                    score = 0
                    continue
                res.append(ModelDetectorResult(
                    token_seq.merge([(chunk_start, chunk_end)], lambda seq: ModelToken(str(seq.trim()))),
                    ModelToken(str(token_seq.get_sub(chunk_start, chunk_end).trim())),
                    score=score
                ))
                score = 0
        return ModelSelector().select(res)


class ModelSelector(BaseSelector[ModelDetectorResult]):
    def select(self, results: list[ModelDetectorResult]) -> ModelDetectorResult:
        # TODO banned
        if not results:
            return ModelDetectorResult(None, None, 0)
        return max(results, key=lambda result: self.score_model(result.model, results.index(result)))

    def score_model(self, model: ModelToken, index: int):
        score = 0
        chars = set(model.value)
        score += 6 if AsciiToken.char_set & chars else 0
        score += 5 if DigitToken.char_set & chars else 0
        score += 3 if any(c.isupper() for c in chars) else 0
        score += 4 if index == 0 else 0
        return score
