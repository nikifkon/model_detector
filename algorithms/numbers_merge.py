import json
from typing_extensions import Self
from algorithms.base import BaseLogEntry, TokenBasedAlgorithm, NewSequenceResult
from tokens import BreakToken, Token, TokenSeq, DigitToken


class NumberToken(Token):
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
        for context, token in seq.iter_with_context():
            if cont:
                if isinstance(token, DigitToken) and sep1(context.left_sep):
                    count_of_digits += 1
                    res.logs.sep1.append(context.left_sep)
                    continue
                elif count_of_digits > 0 and (sep2(context.left_sep) or isinstance(token, BreakToken)):
                    res.logs.sep2.append(context.left_sep)
                    chunks.append((chank_start, context.token_index))
                    cont = False
                    chank_start = None
                else:
                    res.logs.sep0.pop()
                    for _ in range(count_of_digits):
                        res.logs.sep1.pop()
                    cont = False
                    chank_start = None

            if not cont:
                if isinstance(token, DigitToken) and (sep0(context.left_sep) or context.token_index == 0):
                    res.logs.sep0.append(context.left_sep)
                    cont = True
                    chank_start = context.token_index
                    count_of_digits = 0

        # merge
        res.seq = seq.merge(chunks, lambda x: NumberToken(str(x)))
        return res
