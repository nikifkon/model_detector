import json
from typing_extensions import Self
from algorithms.base import BaseLogEntry, TokenBasedAlgorithm, NewSequenceResult
from tokens import BreakToken, ValueToken, TokenSeq, DigitToken, Sep


class NumberToken(ValueToken):
    pass


class NumberMergeLog(BaseLogEntry):
    sep0: list[str]
    sep1: list[str]
    sep2: list[str]

    def __init__(self, sep0=None, sep1=None, sep2=None):
        self.sep0 = [] if sep0 is None else sep0
        self.sep1 = [] if sep1 is None else sep1
        self.sep2 = [] if sep2 is None else sep2

    def dump_data(self) -> str:
        return json.dumps({
            'sep0': self.sep0,
            'sep1': self.sep1,
            'sep2': self.sep2
        }, ensure_ascii=False)

    @classmethod
    def load_data(cls, dump: str) -> Self:
        data = json.loads(dump)
        return cls(data['sep0'], data['sep1'], data['sep2'])

    def __eq__(self, obj: 'NumberMergeLog') -> bool:
        return self.sep0 == obj.sep0 and self.sep1 == obj.sep1 and self.sep2 == obj.sep2

    def __repr__(self):
        return f'"{"".join(self.sep0)};{"".join(self.sep1)};{"".join(self.sep2)}"'


class NumberMergeResult(NewSequenceResult[NumberMergeLog]):
    def __init__(self, *args, **kwargs):
        self.logs = NumberMergeLog()
        super().__init__(*args, **kwargs)


class NumbersMerge(TokenBasedAlgorithm[NumberMergeResult]):
    def parse_by_tokens(self, seq: TokenSeq) -> NumberMergeResult:
        """
        {sep0}{digit}({sep1}{digit})+{sep2}

        logs:
        - sep0, sep1, sep2
        """
        def sep2(sep):
            return True

        def sep1(sep):
            return sep in set('×-,./')

        def sep0(sep):
            return sep not in set(['', '-'])

        res = NumberMergeResult()
        # find
        cont = False
        chunks: list[tuple[int, int]] = []
        chank_start = None

        count_of_digits = 0

        g = seq.generate_with_context()
        for context, token in g:
            if cont:
                if isinstance(token, Sep) and sep1(token.value):
                    res.logs.sep1.append(token.value)
                    next_context, next_token = g.send(+1)
                    if isinstance(next_token, DigitToken):
                        count_of_digits += 1
                        continue
                    else:
                        res.logs.sep1.pop()

                if count_of_digits > 0 and (isinstance(token, BreakToken) or (isinstance(token, Sep) and (sep2(token.value) or isinstance(next_token, BreakToken)))):
                    res.logs.sep2.append(token.value)
                    chunks.append((chank_start, context.value_index + (not isinstance(token, ValueToken))))
                    cont = False
                    chank_start = None
                else:
                    res.logs.sep0.pop()
                    for _ in range(count_of_digits):
                        res.logs.sep1.pop()
                    cont = False
                    chank_start = None
            if not cont:
                if isinstance(token, DigitToken) and (context.token_index == 0 or (isinstance(context.prev, Sep) and sep0(context.prev.value))):
                    if context.prev:
                        res.logs.sep0.append(context.prev.value)
                    cont = True
                    chank_start = context.value_index
                    count_of_digits = 0

        # merge
        res.seq = seq.merge(chunks, lambda x: NumberToken(str(x)))
        return res
