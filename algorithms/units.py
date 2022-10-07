from itertools import chain
from algorithms.base import (EmptyLog, NewSequenceResult, TokenBasedAlgorithm)
from tokens import DigitToken, TokenSeq, CharToken, Sep
from data.units import UNIT_MAP, SUFFIXES, PREFIXES


class Unit(CharToken):
    def __init__(self, value):
        self.is_valid, data = self.try_parse(value)
        (self.prefix, self.norm, self.suffix) = data
        value = ""
        if self.prefix:
            value += self.prefix
        value += self.norm
        if self.suffix:
            value += self.suffix
        self.banned = self.is_valid and 'banned' in UNIT_MAP[self.norm.lower()]
        super().__init__(value)

    def try_parse(self, unit: str, prefix: str = None, suffix: str = None) -> tuple[bool, tuple[str, str, str]]:
        if unit.lower() in UNIT_MAP.keys():
            if suffix and not UNIT_MAP[unit.lower()]["allow_suffix"]:
                return False, (prefix, unit, suffix)
            if prefix and not UNIT_MAP[unit.lower()]["allow_prefix"]:
                return False, (prefix, unit, suffix)
            return True, (prefix, unit, suffix)
        if not suffix:
            for suf_key, suf_val in SUFFIXES.items():
                if suf_key in unit and suf_key == unit[-len(suf_key):]:
                    return self.try_parse(unit[:-len(suf_key)], prefix, suf_val)
        if not prefix:
            for p in PREFIXES:
                if p in unit and p == unit[:len(p)]:
                    return self.try_parse(unit[len(p):], p, suffix)
        return False, ('', '', '')

    def get_prop_name(self) -> str:
        if self.is_valid:
            return UNIT_MAP[self.norm.lower()]["name"]


class UnitExpression(Unit):
    valid_operators = set('./×')

    def __init__(self, seq: TokenSeq):
        self.seq = self.handle_units(seq)
        self.is_valid = not (len(seq.tokens) == 1 and seq.tokens[0].banned)
        self.value = str(self.seq)

    def handle_units(self, seq: TokenSeq) -> TokenSeq:
        norm = []
        for context, token in seq.iter_with_context():
            if token.value == '.':
                if isinstance(context.next, Unit):
                    norm.append(Sep('/'))
                else:
                    pass
            else:
                norm.append(token)
        return TokenSeq(norm)


class UnitMerge(TokenBasedAlgorithm[NewSequenceResult[EmptyLog]]):
    """
    unit_exp = {unit}({operator}{unit})*
    unit = {prefix}{u}{suffix}
    """
    def __init__(self):
        pass

    def parse_by_tokens(self, token_seq: TokenSeq) -> NewSequenceResult[EmptyLog]:
        res = []

        source = token_seq.iter_with_context()
        res = []
        try:
            while nxt := next(source):
                context, token = nxt
                if (unit := Unit(token.value)).is_valid:
                    if context.next.value == '^':
                        context2, token2 = next(source)
                        if isinstance(context.next, DigitToken):
                            _, token3 = next(source)
                            unit = Unit(token.value + token2.value + token3.value)
                            assert unit.is_valid
                        else:
                            source = chain((context2, token2), source)

                    elif isinstance(context.next, DigitToken):
                        _, token3 = next(source)
                        unit = Unit(token.value + token3.value)
                        assert unit.is_valid

                    res.append(unit)
                else:
                    res.append(token)
        except StopIteration:
            temp_seq = TokenSeq(res)

        cont = False
        skipped_tokens = []
        res = []
        units = []

        for context, token in temp_seq.iter_with_context():
            if cont:
                if isinstance(token, Unit):
                    units.append(token)

                    skipped_tokens.append(token)
                if isinstance(token, Sep) and token.value in UnitExpression.valid_operators:
                    units.append(token)
                    skipped_tokens.append(token)

                else:
                    prefix_len = len(units)
                    while prefix_len > 0:
                        unit_exp = UnitExpression(TokenSeq(units[:prefix_len]))
                        if unit_exp.is_valid:
                            break
                        prefix_len -= 1
                    if prefix_len > 0:
                        res.append(unit_exp)
                    else:
                        res.extend(skipped_tokens)
                    cont = False
                    units.clear()
            elif not cont:
                if isinstance(token, Unit):
                    cont = True
                    units.append(token)
                    skipped_tokens = [token]
                else:
                    res.append(token)
        return NewSequenceResult(TokenSeq(res))
