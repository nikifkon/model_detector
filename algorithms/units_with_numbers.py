from typing_extensions import Self
from algorithms.base import (BaseResult, TokenBasedAlgorithm, BaseLogEntry)
from algorithms.numbers_merge import NumberToken
from algorithms.units import Unit, UnitExpression
from tokens import DigitToken, Token, TokenSeq, Sep


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

        new_tokens = []

        g = token_seq.generate_with_context()
        for context, token in g:
            if (is_digit := isinstance(token, DigitToken)) or (is_number := isinstance(token, NumberToken)):
                value_token = token
                if isinstance(context.next, Sep) and (is_digit and self.is_digit_sep(context.next.value)) or (is_number and self.is_number_sep(context.next.value)):
                    context, token = g.send(+1)
                if isinstance(context.next, UnitExpression) or isinstance(context.next, Unit):
                    new_tokens.pop()
                    prop = UnitProperty(value_token, context.next)
                    new_tokens.append(prop)
                    res.units.add(prop)
                    continue
                else:
                    new_tokens.append(value_token)
                    continue
            new_tokens.append(token)
        res.seq = TokenSeq(new_tokens)
        return res

    def is_number_sep(self, sep):
        return ')' not in sep

    def is_digit_sep(self, sep):
        return ')' not in sep
