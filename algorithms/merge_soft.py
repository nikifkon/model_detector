from dataclasses import dataclass

from algorithms.base import TokenBasedAlgorithm, NewSequenceResult
from tokens import ValueToken, TokenSeq, Token


class MergedToken(ValueToken):
    @classmethod
    def from_pair(cls, t1: Token, t2: Token, sep: str = '-'):
        return cls(t1.value + sep + t2.value)


@dataclass(eq=True, frozen=True)
class MergeSoftResult(NewSequenceResult):
    pass


class DigitTokens:
    pass


class MergeSoft(TokenBasedAlgorithm[MergeSoftResult]):
    soft_seps = {'-', '. '}
    excepts = (DigitTokens,)
    musts = (ValueToken,)

    def parse_by_tokens(self, seq: TokenSeq) -> MergeSoftResult:
        new_tokens = []
        gen = seq.generate_with_context()
        for context, token in gen:
            if token.value in self.soft_seps and \
                    context.prev and isinstance(context.prev, self.musts) and not isinstance(context.prev, self.excepts) \
                    and context.next and isinstance(context.next, self.musts) and not isinstance(context.next, self.excepts):
                _, next_token = gen.send(+1)
                merged = MergedToken.from_pair(new_tokens.pop(), next_token, sep=token.value)
                new_tokens.append(merged)
            else:
                new_tokens.append(token)
        return NewSequenceResult(None, TokenSeq(new_tokens))
