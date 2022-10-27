from algorithms.base import (EmptyLog, NewSequenceResult, TokenBasedAlgorithm)
from tokens import DigitToken, TokenSeq, CharToken, Sep, BreakToken, Token
from data.units import UNIT_MAP, SUFFIXES, PREFIXES


class Unit(CharToken):
    def __init__(self, value):
        self.old_value = value
        self.is_valid, data = self.try_parse(value.lower())
        (self.prefix, self.norm, self.suffix) = data
        if self.prefix == 'куб.':
            self.prefix = None
            self.suffix = '^3'
        elif self.prefix == 'кв.':
            self.prefix = None
            self.suffix = '^2'
        value = ""
        if self.prefix:
            value += self.prefix
        value += self.norm
        if self.suffix:
            value += self.suffix
        self.banned = self.is_valid and 'banned' in UNIT_MAP[self.norm.lower()]
        super().__init__(value)

    @classmethod
    def from_seq(cls, seq: TokenSeq):
        obj = cls(str(seq))
        obj.old_seq = seq
        return obj

    def try_parse(self, unit: str, prefix: str = None, suffix: str = None) -> tuple[bool, tuple[str, str, str]]:
        if unit.lower() in UNIT_MAP.keys():
            if suffix and not UNIT_MAP[unit.lower()]["allow_suffix"]:
                return False, (prefix, unit, suffix)
            if prefix and not UNIT_MAP[unit.lower()]["allow_prefix"]:
                return False, (prefix, unit, suffix)
            unit = UNIT_MAP[unit.lower()]['standard']
            return True, (prefix, unit, suffix)
        if not suffix:
            for suf_key, suf_val in SUFFIXES.items():
                if suf_key in unit and suf_key == unit[-len(suf_key):]:
                    return self.try_parse(unit[:-len(suf_key)], prefix, suf_val)
        if not prefix:
            for p in PREFIXES:
                p = p.lower()
                if p in unit and p == unit[:len(p)]:
                    return self.try_parse(unit[len(p):], p, suffix)
        return False, ('', '', '')

    def get_prop_name(self) -> str:
        if self.is_valid:
            return UNIT_MAP[self.norm.lower()]["name"]

    def to_original(self) -> list[Token]:
        return [t for t in TokenSeq.from_string(self.old_value).iter_by_tokens() if not isinstance(t, BreakToken)]


class UnitExpression(Unit):
    valid_operators = set('./×')

    @classmethod
    def from_seq(cls, seq: TokenSeq):
        seq = cls.handle_units(seq)
        obj = cls(str(seq))
        obj.is_valid = not (len([token for token in seq.iter_by_tokens() if isinstance(token, Unit)]) == 1 and seq.tokens[0].banned)

        obj.old_seq = seq
        return obj

    def to_original(self) -> list[Token]:
        old_seq_ = []
        for token in self.old_seq.iter_by_tokens():
            if isinstance(token, Unit):
                old_seq_.extend(token.to_original())
            elif isinstance(token, BreakToken):
                continue
            else:
                old_seq_.append(token)
        return old_seq_

    @staticmethod
    def handle_units(seq: TokenSeq) -> TokenSeq:
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

    def get_prop_name(self) -> str:
        if self.is_valid:
            if self.norm.lower() not in UNIT_MAP:
                print(f"{self.norm.lower()} not exit")
                return '???'
            return UNIT_MAP[self.norm.lower()]["name"]


class UnitMerge(TokenBasedAlgorithm[NewSequenceResult[EmptyLog]]):
    """
    unit_exp = {unit}({operator}{unit})*{end_condition}
    unit = {prefix}{u}{suffix}
    """

    def __init__(self):
        pass

    def end_condition(self, token):
        return isinstance(token, Sep)

    def parse_by_tokens(self, token_seq: TokenSeq) -> NewSequenceResult[EmptyLog]:
        source = token_seq.generate_with_context()
        res = []
        for context, token in source:
            if Unit(token.value).is_valid:
                token2 = None
                token3 = None
                if context.next.value == '^':
                    context, token2 = source.send(+1)
                if isinstance(context.next, DigitToken) and context.next.value in ['2', '3']:
                    context, token3 = source.send(+1)
                unit = Unit.from_seq(TokenSeq([token, token2, token3]))
                # unit = Unit(token.value + (token2.value if token2 else '') + (token3.value if token3 else ''))
                if not unit.is_valid or not self.end_condition(context.next):
                    res.append(token)
                    if token2:
                        res.append(token2)
                    if token3:
                        res.append(token3)
                    continue

                res.append(unit)
            else:
                res.append(token)
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
                        unit_exp = UnitExpression.from_seq(TokenSeq(units[:prefix_len]))
                        if unit_exp.is_valid:
                            break
                        prefix_len -= 1
                    if prefix_len > 0:
                        res.append(unit_exp)
                    else:
                        res.extend(skipped_tokens)
                    cont = False
                    units.clear()
            if not cont:
                if isinstance(token, Unit):
                    cont = True
                    units.append(token)
                    skipped_tokens = [token]
                else:
                    res.append(token)
        return NewSequenceResult(None, TokenSeq(res))
