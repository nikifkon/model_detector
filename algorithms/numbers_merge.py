import json
import re
from dataclasses import dataclass
from typing_extensions import Self

from algorithms.base import BaseLogEntry, TokenBasedAlgorithm, NewSequenceResult
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

    def to_original(self):
        self.value = self.old_value


class NumberMergeLog(BaseLogEntry):
    start: list[str]
    sep1: list[str]
    end: list[str]

    def __init__(self, sep0=None, sep1=None, end=None):
        self.start = [] if sep0 is None else sep0
        self.sep1 = [] if sep1 is None else sep1
        self.end = [] if end is None else end

    def dump_data(self) -> str:
        return json.dumps({
            'start': self.start,
            'sep1': self.sep1,
            'end': self.end
        }, ensure_ascii=False)

    @classmethod
    def load_data(cls, dump: str) -> Self:
        data = json.loads(dump)
        return cls(data['start'], data['sep1'], data['end'])

    def __eq__(self, obj: 'NumberMergeLog') -> bool:
        return self.start == obj.start and self.sep1 == obj.sep1 and self.end == obj.end

    def __repr__(self):
        return f'"{"".join(self.start)};{"".join(self.sep1)};{"".join(self.end)}"'


@dataclass(eq=True, frozen=True)
class NumberMergeResult(NewSequenceResult[NumberMergeLog]):
    pass


class NumbersMerge(TokenBasedAlgorithm[NumberMergeResult]):
    """
    {start}{digit}({sep1}{digit})+{end}

    logs:
    - start, sep1, end
    """
    def end(self, token: Token):
        return True

    def sep1(self, sep):
        return sep in set('×-,./…')

    def start(self, token: Token):
        return isinstance(token, Sep) and token.value not in {'', '-'}

    def parse_by_tokens(self, seq: TokenSeq) -> NumberMergeResult:
        res_log = NumberMergeLog()
        # find
        cont = False
        chunks: list[tuple[int, int]] = []
        chunk_start = None

        count_of_digits = 0

        g = seq.generate_with_context()
        for context, token in g:
            if cont:
                if isinstance(token, Sep) and self.sep1(token.value):
                    res_log.sep1.append(token.value)
                    next_context, next_token = g.send(+1)
                    if isinstance(next_token, DigitToken):
                        count_of_digits += 1
                        continue
                    else:
                        res_log.sep1.pop()

                # if count_of_digits > 0 and (isinstance(token, BreakToken) or (isinstance(token, Sep) and (end(token.value) or isinstance(next_token, BreakToken)))):
                if count_of_digits > 0 and self.end(token):
                    res_log.end.append(token.value)
                    chunks.append((chunk_start, context.value_index + (not isinstance(token, ValueToken))))
                    cont = False
                    chunk_start = None
                else:
                    if res_log.start:
                        res_log.start.pop()
                    for _ in range(count_of_digits):
                        res_log.sep1.pop()
                    cont = False
                    chunk_start = None
            if not cont:
                if isinstance(token, DigitToken) and (context.token_index == 0 or self.start(context.prev)):
                    if context.prev:
                        res_log.start.append(context.prev.value)
                    cont = True
                    chunk_start = context.value_index
                    count_of_digits = 0

        # merge
        res_seq = seq.merge(chunks, lambda x: NumberToken(str(x)))
        return NumberMergeResult(res_log, res_seq)
