from algorithms.base import BaseSelector, TokenBasedAlgorithm, BaseResult
from tokens import TokenSeq


class PossibleResults(BaseResult):
    order_list: list[TokenSeq]

    def __init__(self, order_list: list[TokenSeq]):
        self.order_list = order_list


class ListPossibleSubModels(TokenBasedAlgorithm[PossibleResults]):
    def parse_by_tokens(self, token_seq: TokenSeq) -> PossibleResults:
        for token in token_seq:
            pass
            # if '/' in token.right_sep:
            #     token.right_sep = None
            #     cur.append(token)
            #     sub_models.append(cur)
            #     cur = []
            # else:
            #     cur.append(token)
        return PossibleResults([])


class SelectSubModel(BaseSelector[PossibleResults]):
    def select(self, possibilities: PossibleResults):
        pass
