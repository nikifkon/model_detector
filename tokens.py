from abc import ABCMeta
from typing import Callable, NamedTuple
from io import StringIO
from string import ascii_letters, digits
from itertools import pairwise, chain


class Token(metaclass=ABCMeta):
    def __init__(self, value: str):
        self.value = value

    def str(self):
        return self.value

    def __repr__(self):
        return self.value


class BreakToken(Token):
    def __init__(self):
        super().__init__('')

    def __repr__(self):
        return ""


class DigitToken(Token):
    char_set = set(digits)


class CharToken(Token, metaclass=ABCMeta):
    pass


class AsciiToken(CharToken):
    char_set = set(ascii_letters)


class CyrillicToken(CharToken):
    char_set = set("АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя")


class SpecialToken(Token):
    char_set = set("+")


class TokenSeq:
    def __init__(self, tokens: list[Token], seps: list[str]):
        assert len(tokens) == len(seps)
        self.tokens = tokens
        self.seps = seps

    @classmethod
    def from_string(self, input: str):
        cur = StringIO()
        prev_type = None
        tokens: list[Token] = []
        seps: list[str] = []

        for i, c in enumerate(chain(input, [''])):
            cur_type = None
            if c == '':
                cur_type = 'end'
            elif c in DigitToken.char_set:
                cur_type = DigitToken
            elif c in AsciiToken.char_set:
                cur_type = AsciiToken
            elif c in CyrillicToken.char_set:
                cur_type = CyrillicToken
            elif c in SpecialToken.char_set:
                cur_type = SpecialToken

            if prev_type == cur_type:
                cur.write(c)
            else:
                if prev_type is None:
                    left_sep = cur.getvalue()
                    seps.append(left_sep)
                else:
                    if cur_type is not None:
                        seps.append('')
                    value = cur.getvalue()
                    new_token = prev_type(value)
                    tokens.append(new_token)
                cur = StringIO()
                cur.write(c)
            prev_type = cur_type

        tokens.append(BreakToken())
        return TokenSeq(tokens, seps)

    def iter_with_context(self):
        context = NamedTuple('Context', [('prev', Token), ('next', Token), ('left_sep', str), ('right_sep', str), ('token_index', int)])
        for i, token in enumerate(self.tokens):
            yield context(
                self.tokens[i - 1] if i - 1 >= 0 else None,
                self.tokens[i + 1] if i + 1 < len(self.tokens) else None,
                self.seps[i],
                self.seps[i + 1] if i + 1 < len(self.seps) else None,
                i
            ), token

    def iter_pairwise(self):
        for i, token in enumerate(pairwise(self.tokens)):
            yield i, token

    def merge(self, chunks: list[tuple[int, int]], merge_seq: Callable[['Span'], Token]) -> 'TokenSeq':
        # assert end < len(self.tokens)  # can't merge BreakToken TODO validate
        new_tokens = []
        new_seps = []

        span_tokens = []
        span_seps = []
        chunks_todo = chunks.copy()
        for i, token in enumerate(self.tokens):
            if len(chunks_todo) == 0 or (i < chunks_todo[0][0] or chunks_todo[0][1] < i):
                new_seps.append(self.seps[i])
                new_tokens.append(token)
            elif chunks_todo[0][0] <= i and i < chunks_todo[0][1]:
                if chunks_todo[0][0] == i:
                    new_seps.append(self.seps[i])
                else:
                    span_seps.append(self.seps[i])
                span_tokens.append(token)

                if i == chunks_todo[0][1] - 1:
                    new_token = merge_seq(Span(span_tokens, span_seps))
                    new_tokens.append(new_token)
                    span_tokens.clear()
                    span_seps.clear()
                    chunks_todo.pop(0)
        return TokenSeq(new_tokens, new_seps)

    def __str__(self):
        assert len(self.seps) == len(self.tokens)
        cur = StringIO()
        for token, sep in zip(self.tokens, self.seps):
            cur.write(sep)
            cur.write(token.value)
        return cur.getvalue()

    def __repr__(self):
        return str(self)


class Span():
    def __init__(self, tokens: list[Token], seps: list[str]):
        assert len(seps) + 1 == len(tokens)
        self.tokens = tokens
        self.seps = seps

    def __str__(self):
        assert len(self.seps) + 1 == len(self.tokens)
        cur = StringIO()
        cur.write(self.tokens[0].value)
        for token, sep in zip(self.tokens[1:], self.seps):
            cur.write(sep)
            cur.write(token.value)
        return cur.getvalue()

    def __repr__(self):
        return str(self)
