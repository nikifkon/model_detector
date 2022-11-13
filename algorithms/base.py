from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from tokens import TokenSeq


@dataclass(eq=True, frozen=True)
class BaseResult(metaclass=ABCMeta):
    pass


TResult = TypeVar('TResult', bound=BaseResult)


class BaseAlgorithm(Generic[TResult], metaclass=ABCMeta):

    @abstractmethod
    def parse(self, input: str) -> TResult:
        pass


class TokenBasedAlgorithm(BaseAlgorithm[TResult]):
    @staticmethod
    def get_tokens(input: str) -> TokenSeq:
        return TokenSeq.from_string(input)

    def parse(self, input: str) -> TResult:
        tokens = self.get_tokens(input)
        return self.parse_by_tokens(tokens)

    @abstractmethod
    def parse_by_tokens(self, token_seq: TokenSeq) -> TResult:
        pass


class BaseSelector(Generic[TResult], metaclass=ABCMeta):

    @abstractmethod
    def select(self, input: list[TResult]) -> TResult:
        pass


@dataclass(eq=True, frozen=True)
class NewSequenceResult(BaseResult):
    seq: TokenSeq

    # def __init__(self, seq: TokenSeq = None, **kwags):
    #     self.seq = seq
    #     super().__init__(**kwags)
