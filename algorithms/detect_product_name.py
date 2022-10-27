from dataclasses import dataclass
from typing import Callable

from algorithms.base import NewSequenceResult, TokenBasedAlgorithm, BaseSelector
from data.dictionary import is_token_in_cyrillic_dictionary
from tokens import BreakToken, TokenSeq, ProductNameToken, Token, Sep, Context


@dataclass(eq=True, frozen=True)
class ProductNameFinderResult(NewSequenceResult):
    product_name: ProductNameToken


class ProductNameFinder(TokenBasedAlgorithm[ProductNameFinderResult]):
    def __init__(self, is_banned: Callable[[TokenSeq], bool]):
        self.is_banned = is_banned

    def main_condition(self, context: Context, token: Token):
        return is_token_in_cyrillic_dictionary(context, token)

    def parse_by_tokens(self, token_seq: TokenSeq) -> ProductNameFinderResult:
        res: list[ProductNameFinderResult] = []
        gen = token_seq.generate_with_context()
        for context, token in gen:
            chunk_start = context.value_index
            if self.main_condition(context, token):
                while (self.main_condition(context, token) or isinstance(token, Sep)) and not isinstance(token, BreakToken):
                    context, token = gen.send(+1)
                chunk_end = context.value_index + isinstance(token, BreakToken)
                res.append(ProductNameFinderResult(
                    None,
                    token_seq.merge([(chunk_start, chunk_end)], lambda seq: ProductNameToken(str(seq.trim()))),
                    ProductNameToken(str(token_seq.get_sub(chunk_start, chunk_end).trim()))
                ))
        res.append(ProductNameFinderResult(None, token_seq, None))  # default res
        return ProductNameSelector().select(res)


class ProductNameSelector(BaseSelector[ProductNameFinderResult]):
    def select(self, input: list[ProductNameFinderResult]) -> ProductNameFinderResult:
        return input[0]
