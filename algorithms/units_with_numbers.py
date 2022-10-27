from dataclasses import dataclass
from typing import Iterable

from algorithms.base import NewSequenceResult, TokenBasedAlgorithm
from algorithms.numbers_merge import NumberToken
from algorithms.units import Unit, UnitExpression
from data.units import PROPERTY_NAMES
from tokens import DigitToken, Token, TokenSeq, Sep, DataToken, Context


class UnitProperty(DataToken):
    def __init__(self, property_value: Token, unit: Unit, property_name):
        self.property_value = property_value
        self.unit = unit
        if not property_name:
            property_name = self.unit.get_prop_name()
        self.property_name = property_name
        self.value = f'{str(property_value)} {str(unit)}'

    @classmethod
    def to_dict(cls, collection: Iterable['UnitProperty']):
        return {prop.property_name: (prop.property_value.value, prop.unit.value) for prop in collection}


# class UnitLog(BaseLogEntry):
#     def dump_data(self) -> str:
#         return {}

#     @classmethod
#     def load_data(cls, dump: str) -> Self:
#         return cls()


@dataclass(eq=True, frozen=True)
class UnitExtractorResult(NewSequenceResult):
    units: set[UnitProperty]


class UnitExtractor(TokenBasedAlgorithm[UnitExtractorResult]):
    """
    {start_condition}{unit}{end_condition}

    start_condition:
    space + Digit
    """

    def __init__(self):
        pass

    def parse_by_tokens(self, token_seq: TokenSeq) -> UnitExtractorResult:
        res_log = None
        new_tokens = []
        res_units = set()

        g = token_seq.generate_with_context()
        for context, token in g:
            if self.start_condition(context, token):
                prop_name = None
                if isinstance(context.prev, Sep) and self.is_property_sep(context.prev.value):
                    prev_context, prev_token = g.send(-1)
                    if prev_context.prev and (key := prev_context.prev.value.lower()) in PROPERTY_NAMES:
                        prop = PROPERTY_NAMES[key]
                        prop_name = prop["standard"]
                        new_tokens.pop()
                        new_tokens.pop()
                    g.send(+1)
                value_token = token
                if isinstance(context.next, Sep) and self.is_number_sep(context.next.value):
                    context, token = g.send(+1)
                if isinstance(context.next, UnitExpression) or isinstance(context.next, Unit):
                    _, unit = g.send(+1)
                    prop = UnitProperty(value_token, unit, prop_name)
                    new_tokens.append(prop)
                    res_units.add(prop)
                    continue
                else:
                    new_tokens.append(value_token)
                    if token != value_token:
                        new_tokens.append(token)
                    continue
            else:
                new_tokens.append(token)
        res_seq = TokenSeq(new_tokens)
        return UnitExtractorResult(res_log, self.unmerge_units(res_seq), frozenset(res_units))

    def start_condition(self, context: Context, token: Token):
        # return (context.token_index <= 0 or isinstance(context.prev, Sep) and (
        #         ' ' in context.prev.value or '(' in context.prev.value)) and isinstance(token, DigitToken)
        return (context.token_index <= 0 or isinstance(context.prev, Sep) and (
                self.is_property_sep(context.prev.value) or self.is_number_start_sep(
                    context.prev.value))) and isinstance(token, DigitToken)

    def is_number_sep(self, sep):
        return ')' not in sep

    def is_number_start_sep(self, sep: str):
        return ' ' in sep or '(' in sep

    def is_property_sep(self, sep: str):
        return sep.strip() in {'=', '.', '', '('}

    def unmerge_units(self, seq: TokenSeq) -> TokenSeq:
        new_tokens = []
        for token in seq.iter_by_tokens():
            # if isinstance(token, UnitExpression):
            #     tokens = token.old_seq.iter_by_tokens()
            # else:
            #     tokens = [token]
            # for sub_token in [token]:
            if isinstance(token, NumberToken):
                token.to_original()
                new_tokens.append(token)
                # new_tokens.extend([token for token in TokenSeq.from_string(token.old_value).iter_by_tokens() if
                #                    not isinstance(token, BreakToken)])
            elif isinstance(token, Unit):
                new_tokens.extend(token.to_original())
            else:
                new_tokens.append(token)
        return TokenSeq(new_tokens)
