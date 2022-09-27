import typing
from io import StringIO
from string import ascii_letters, digits
from itertools import pairwise, chain


class Token:
    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return self.value


class DigitToken(Token):
    char_set = set(digits)


class AsciiToken(Token):
    char_set = set(ascii_letters)


class CyrillicToken(Token):
    char_set = set("АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя")


class SpecialToken(Token):
    char_set = set("+")


class TokenSeq:
    def __init__(self, tokens: list[Token], seps: list[str]):
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

        return TokenSeq(tokens, seps)

    def iter_with_context(self):
        context = typing.NamedTuple('Context', [('prev', Token), ('next', Token), ('left_sep', str), ('right_sep', str), ('token_index', int)])
        for i, token in enumerate(self.tokens):
            yield context(
                self.tokens[i - 1] if i - 1 >= 0 else None,
                self.tokens[i + 1] if i + 1 < len(self.tokens) else None,
                self.seps[i],
                self.seps[i + 1],
                i
            ), token

    def iter_pairwise(self):
        for i, token in enumerate(pairwise(self.tokens)):
            yield i, token

    def __str__(self):
        assert len(self.seps) == len(self.tokens) + 1
        cur = StringIO()
        cur.write(self.seps[0])
        for token, sep in zip(self.tokens, self.seps[1:]):
            cur.write(token.value)
            cur.write(sep)
        return cur.getvalue()

    def __repr__(self):
        return str(self)
