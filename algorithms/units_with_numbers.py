from dataclasses import dataclass
from algorithms.base import NewSequenceResult, TokenBasedAlgorithm
from algorithms.numbers_merge import NumberToken
from algorithms.units import Unit, UnitExpression
from tokens import DigitToken, Token, TokenSeq, Sep


class Property(Token):
    pass


class UnitProperty(Property):
    def __init__(self, property_value: Token, unit: Unit):
        self.property_value = property_value
        self.unit = unit
        self.value = f'{str(property_value)} {str(unit)}'

    @classmethod
    def to_dict(self, collection: list['UnitProperty']):
        return {prop.unit.get_prop_name(): [prop.property_value.value. prop.unit.value] for prop in collection}


# class UnitLog(BaseLogEntry):
#     def dump_data(self) -> str:
#         return {}

#     @classmethod
#     def load_data(cls, dump: str) -> Self:
#         return cls()


@dataclass
class UnitExtractorResult(NewSequenceResult):
    units: set[UnitProperty]


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
        res_log = None
        new_tokens = []
        res_units = set()

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
                    res_units.add(prop)
                    continue
                else:
                    new_tokens.append(value_token)
                    continue
            new_tokens.append(token)
        res_seq = TokenSeq(new_tokens)
        return UnitExtractorResult(res_log, res_seq, res_units)

    def is_number_sep(self, sep):
        return ')' not in sep

    def is_digit_sep(self, sep):
        return ')' not in sep
