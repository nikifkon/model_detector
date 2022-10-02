from itertools import zip_longest
from algorithms.base import (EmptyLog, NewSequenceResult, TokenBasedAlgorithm)
from tokens import DigitToken, TokenSeq, CharToken
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

    def __init__(self, units: list[Unit], operators: list[str]):
        assert len(units) == len(operators) + 1
        self.is_valid, self.operators = self.norm_operators(operators)
        if self.is_valid and len(operators) == 0 and units[0].banned:
            self.is_valid = False
        self.units = units
        self.value = ''.join(self._iter_zip(map(lambda u: str(u), units), self.operators))

    def norm_operators(self, operators: list[str]) -> tuple[bool, list[str]]:
        norm = []
        is_valid = True
        for operator in operators:
            if operator == '.':
                norm.append('/')
            elif operator in self.valid_operators:
                norm.append(operator)
            else:
                is_valid = False
                norm.append(operator)
        return is_valid, norm

    def _iter_zip(self, g1, g2):
        for el1, el2 in zip_longest(g1, g2):
            if el1 is not None:
                yield el1
            if el2 is not None:
                yield el2


class UnitMerge(TokenBasedAlgorithm[NewSequenceResult[EmptyLog]]):
    """
    unit_exp = {unit}({operator}{unit})*
    unit = {prefix}{u}{suffix}
    """
    def __init__(self):
        pass

    def parse_by_tokens(self, token_seq: TokenSeq) -> NewSequenceResult[EmptyLog]:
        new_tokens = []
        new_seps = []
        to_skip = False
        for context, token in token_seq.iter_with_context():
            if to_skip:
                to_skip = False
                continue
            if (u := Unit(token.value)).is_valid:  # TODO use some cast iterface
                new_seps.append(context.left_sep)
                if isinstance(context.next, DigitToken) and (u2 := Unit(token.value + context.next.value)).is_valid:
                    new_tokens.append(u2)
                    to_skip = True
                new_tokens.append(u)
            else:
                new_seps.append(context.left_sep)
                new_tokens.append(token)

        temp_seq = TokenSeq(new_tokens, token_seq.seps)

        cont = False

        skipped_tokens = []
        skipped_seps = []

        new_tokens = []
        new_seps = []

        units = []
        operators = []
        for context, token in temp_seq.iter_with_context():
            if cont:
                if isinstance(token, Unit):
                    operators.append(context.left_sep)
                    units.append(token)

                    skipped_tokens.append(context.left_sep)
                    skipped_seps.append(token)

                else:
                    prefix_len = len(units)
                    while prefix_len > 0:
                        unit_exp = UnitExpression(units[:prefix_len], operators[:prefix_len - 1])
                        if unit_exp.is_valid:
                            break
                        prefix_len -= 1
                    if prefix_len > 0:
                        new_tokens.append(unit_exp)
                        new_seps.append(skipped_seps[0])
                    else:
                        new_tokens.extend(skipped_tokens)
                        new_seps.extend(skipped_seps)
                    cont = False
                    units.clear()
                    operators.clear()
            if not cont:
                if isinstance(token, Unit):
                    cont = True
                    units.append(token)
                    skipped_tokens = [token]
                    skipped_seps = [context.left_sep]
                else:
                    new_seps.append(context.left_sep)
                    new_tokens.append(token)

        return NewSequenceResult(TokenSeq(new_tokens, new_seps))
