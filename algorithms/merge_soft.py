from dataclasses import dataclass

from algorithms.base import TokenBasedAlgorithm, NewSequenceResult
from algorithms.numbers_merge import NumberToken
from tokens import ValueToken, TokenSeq, Token, Sep


class MergedToken(ValueToken):
    @classmethod
    def from_pair(cls, t1: Token, t2: Token, sep: Sep = None):
        return cls(t1.value + (sep.value if sep else '') + t2.value)


@dataclass(eq=True, frozen=True)
class MergeSoftResult(NewSequenceResult):
    pass


class MergeSoft(TokenBasedAlgorithm[MergeSoftResult]):
    soft_seps = {'-', '.'}
    excepts = (NumberToken, )
    musts = (ValueToken,)

    @classmethod
    def can_be_merged(cls, token):
        return isinstance(token, cls.musts) and not isinstance(token, cls.excepts)

    def parse_by_tokens(self, seq: TokenSeq) -> MergeSoftResult:
        new_tokens = []
        gen = seq.generate_with_context()
        for context, token1 in gen:
            token2 = token3 = None
            new_tokens.append(token1)
            if self.can_be_merged(token1) and context.next:
                context2, token2 = gen.send(+1)
                new_tokens.append(token2)
                if isinstance(token2, Sep):
                    if token2.value in self.soft_seps:
                        context3, token3 = gen.send(+1)
                        new_tokens.append(token3)
                    else:
                        continue
                if token3 and self.can_be_merged(token3) or token2 and self.can_be_merged(token2):
                    right = new_tokens.pop()
                    sep = new_tokens.pop() if token3 else None
                    left = new_tokens.pop()
                    merged = MergedToken.from_pair(left, right, sep=sep)
                    new_tokens.append(merged)
        return MergeSoftResult(TokenSeq(new_tokens))
