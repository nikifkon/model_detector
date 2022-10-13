from abc import ABCMeta
from typing import Callable, Iterable, NamedTuple, Generator
from io import StringIO
from string import ascii_letters, digits
from itertools import chain


class Token(metaclass=ABCMeta):
    def __init__(self, value: str):
        self.value = value

    def str(self):
        return self.value

    def __repr__(self):
        return self.value


class Sep(Token):
    pass


class ValueToken(Token, metaclass=ABCMeta):
    pass


class BreakToken(Sep):
    def __init__(self):
        super().__init__('')

    def __repr__(self):
        return ""


class DigitToken(ValueToken):
    char_set = set(digits)


class CharToken(ValueToken, metaclass=ABCMeta):
    pass


class AsciiToken(CharToken):
    char_set = set(ascii_letters)


class CyrillicToken(CharToken):
    char_set = set("АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя")


class SpecialToken(ValueToken):
    char_set = set("+")


Context = NamedTuple('Context', [('prev', Token), ('next', Token), ('token_index', int), ('value_index', int)])


class TokenSeq:
    def __init__(self, tokens: Iterable[Token]):
        self.tokens: tuple[Token] = tuple(tokens)

    @classmethod
    def from_string(self, input: str):
        cur = StringIO()
        prev_type = None
        tokens: list[Token] = []

        for i, c in enumerate(chain(input, [''])):
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
            else:
                cur_type = Sep

            if i == 0 or prev_type == cur_type:
                cur.write(c)
            else:
                value = cur.getvalue()
                new_token = prev_type(value)
                tokens.append(new_token)
                cur = StringIO()
                cur.write(c)
            prev_type = cur_type

        tokens.append(BreakToken())  # TODO нужен ли он?
        return TokenSeq(tokens)

    def iter_by_tokens(self) -> Iterable[Token]:
        for token in self.tokens:
            yield token

    def iter_by_values(self) -> Iterable[ValueToken]:
        for token in self.tokens:
            if isinstance(token, ValueToken):
                yield token

    def iter_with_context(self):
        context = NamedTuple('Context', [('prev', Token), ('next', Token), ('token_index', int), ('value_index', int)])
        value_index = -1
        for token_index, token in enumerate(self.tokens):
            if isinstance(token, ValueToken):
                value_index += 1
            yield context(
                self.tokens[token_index - 1] if token_index - 1 >= 0 else None,
                self.tokens[token_index + 1] if token_index + 1 < len(self.tokens) else None,
                token_index,
                value_index
            ), token

    def generate_with_context(self) -> Generator[type[Context], int, None]:
        value_index = -1
        token_index = 0
        while token_index < len(self.tokens):
            token = self.tokens[token_index]
            if isinstance(token, ValueToken):
                value_index += 1
            offset: int = yield Context(
                self.tokens[token_index - 1] if token_index - 1 >= 0 else None,
                self.tokens[token_index + 1] if token_index + 1 < len(self.tokens) else None,
                token_index,
                value_index
            ), token
            if offset is None:
                token_index += 1
            else:
                token_index += offset

    def iter_ngrams_by_values(self, n: int = 2):
        if n < 1:
            raise ValueError(f'Undefined ngram for n = {n}')

        values = list(self.iter_by_values())
        return [self.get_sub(i, i + n) for i in range(len(values) - (n - 1))]

    def merge(self, chunks: list[tuple[int, int]], merge_seq: Callable[['TokenSeq'], Token]) -> 'TokenSeq':
        # assert end < len(self.tokens)  # can't merge BreakToken TODO validate
        new_tokens = []

        span_tokens = []
        chunks_todo = chunks.copy()
        i = -1
        for token in self.tokens:
            if isinstance(token, ValueToken):
                i += 1
            if len(chunks_todo) == 0 or (i < chunks_todo[0][0] or chunks_todo[0][1] < i):
                new_tokens.append(token)
            elif chunks_todo[0][0] <= i and i < chunks_todo[0][1]:
                span_tokens.append(token)

                if i == chunks_todo[0][1] - 1:
                    new_token = merge_seq(TokenSeq(span_tokens))
                    new_tokens.append(new_token)
                    span_tokens.clear()
                    chunks_todo.pop(0)
        return TokenSeq(new_tokens)

    def get_sub(self, start: int, end: int, index_by_values=True):
        if not index_by_values:
            raise NotImplementedError()
        value_token_counter = -1
        res: list[Token] = []
        for i, token in enumerate(self.tokens):
            if isinstance(token, ValueToken):
                value_token_counter += 1
            if value_token_counter < start:
                continue
            res.append(token)
            if value_token_counter == end - 1:
                return TokenSeq(res)

    def __str__(self):
        cur = StringIO()
        for token in self.tokens:
            cur.write(token.value)
        return cur.getvalue()

    def __repr__(self):
        return str(self)


# class Span():
#     def __init__(self, tokens: list[Token], seps: list[str]):
#         assert len(seps) + 1 == len(tokens)
#         self.tokens = tokens
#         self.seps = seps

#     @classmethod
#     def from_string(self, input: str) -> 'Span':
#         pass

#     @classmethod
#     def from_seq(self, seq: TokenSeq, start: int, end: int) -> 'Span':
#         pass

#     def __str__(self):
#         assert len(self.seps) + 1 == len(self.tokens)
#         cur = StringIO()
#         cur.write(self.tokens[0].value)
#         for token, sep in zip(self.tokens[1:], self.seps):
#             cur.write(sep)
#             cur.write(token.value)
#         return cur.getvalue()

#     def __repr__(self):
#         return str(self)
