import re
from dataclasses import dataclass

from algorithms.base import TokenBasedAlgorithm, NewSequenceResult
from tokens import ValueToken, TokenSeq, DigitToken, Sep, Token


class NumberToken(DigitToken):
    from_to_pattern = re.compile(r'^([\+\-]?[0-9]+)[\-…]([\+\-]?[0-9]+)$')

    def __init__(self, value: str):
        self.old_value = value
        if match := self.from_to_pattern.match(value):
            _from, to = match.groups()
            if float(_from) < float(to):
                super().__init__(f'от {_from} до {to}')
                return
        super().__init__(value)

    @classmethod
    def from_pair(cls, t1: Token, t2: Token, sep: Sep = None):
        return cls(t1.value + sep.value if sep else '' + t2.value)

    def to_original(self):
        self.value = self.old_value


@dataclass(eq=True, frozen=True)
class NumberMergeResult(NewSequenceResult):
    pass


class NumbersMerge(TokenBasedAlgorithm[NumberMergeResult]):
    """
    {start}{digit}({sep1}{digit})+{end}
    """
    def end(self, token: Token):
        return True

    def sep1(self, sep):
        return sep in set('×-,./…')

    def start(self, token: Token):
        return isinstance(token, Sep) and token.value not in {'', '-'}

    def parse_by_tokens(self, seq: TokenSeq) -> NumberMergeResult:
        # find
        cont = False
        chunks: list[tuple[int, int]] = []
        chunk_start = None

        count_of_digits = 0

        g = seq.generate_with_context()
        for context, token in g:
            if cont:
                if isinstance(token, Sep) and self.sep1(token.value):
                    next_context, next_token = g.send(+1)
                    if isinstance(next_token, DigitToken):
                        count_of_digits += 1
                        continue
                    else:
                        pass
                # if count_of_digits > 0 and (isinstance(token, BreakToken) or (isinstance(token, Sep) and (end(token.value) or isinstance(next_token, BreakToken)))):
                if count_of_digits > 0 and self.end(token):
                    chunks.append((chunk_start, context.value_index + (not isinstance(token, ValueToken))))
                    cont = False
                    chunk_start = None
                else:
                    cont = False
                    chunk_start = None
            if not cont:
                if isinstance(token, DigitToken) and (context.token_index == 0 or self.start(context.prev)):
                    cont = True
                    chunk_start = context.value_index
                    count_of_digits = 0

        # merge
        res_seq = seq.merge(chunks, lambda x: NumberToken(str(x)))
        return NumberMergeResult(res_seq)
