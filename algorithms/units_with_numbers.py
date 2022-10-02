from typing_extensions import Self
from algorithms.base import (BaseResult, TokenBasedAlgorithm, BaseLogEntry)
from algorithms.numbers_merge import NumberToken
from algorithms.units import Unit, UnitExpression
from tokens import DigitToken, Token, TokenSeq


class UnitProperty(Token):
    def __init__(self, property_value: Token, unit: Unit):
        self.property_value = property_value
        self.unit = unit
        self.value = f'{str(property_value)} {str(unit)}'

    @classmethod
    def to_dict(self, collection: list['UnitProperty']):
        return {prop.unit.get_prop_name(): [prop.property_value.value. prop.unit.value] for prop in collection}


class UnitLog(BaseLogEntry):
    def dump_data(self) -> str:
        return {}

    @classmethod
    def load_data(cls, dump: str) -> Self:
        return cls()


class UnitExtractorResult(BaseResult):
    seq: str
    units: set[UnitProperty]

    def __init__(self, *args, **kwargs):
        self.logs = UnitLog()
        self.units = set()
        super().__init__(*args, **kwargs)


class UnitExtractor(TokenBasedAlgorithm[UnitExtractorResult]):
    """
    {number}{number_sep}{unit_exp}{end_sep}|{digit}{digit_sep}{unit_exp}{end_sep}|{expression}{expression_sep}{unit_exp}

    logs:
        - value_type: (D)igit, (N)umber, (E)xpression
        - end_sep
        - unit
    """
    def __init__(self):
        pass

    def parse_by_tokens(self, token_seq: TokenSeq) -> UnitExtractorResult:
        res = UnitExtractorResult()
        # find
        cont = False

        new_tokens = []
        new_seps = []

        for context, token in token_seq.iter_with_context():
            if cont:
                if isinstance(token, UnitExpression):
                    new_tokens.pop()
                    prop = UnitProperty(context.prev, token)
                    new_tokens.append(prop)
                    res.units.add(prop)
                    cont = False
                    continue
                elif isinstance(token, Unit):
                    new_tokens.pop()
                    prop = UnitProperty(context.prev, token)
                    new_tokens.append(prop)
                    res.units.add(prop)
                    cont = False
                    continue
                cont = False
            if not cont:
                if isinstance(token, DigitToken) and context.right_sep is not None and self.is_digit_sep(context.right_sep):
                    cont = True
                elif isinstance(token, NumberToken) and context.right_sep is not None and self.is_number_sep(context.right_sep):
                    cont = True
                new_seps.append(context.left_sep)
                new_tokens.append(token)
        res.seq = TokenSeq(new_tokens, new_seps)
        return res

    def is_number_sep(self, sep):
        return ')' not in sep

    def is_digit_sep(self, sep):
        return ')' not in sep
