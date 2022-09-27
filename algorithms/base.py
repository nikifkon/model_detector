from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from tokens import TokenSeq


T = TypeVar('T')


class BaseResult(metaclass=ABCMeta):
    pass


class BaseAlgorithm(Generic[T], metaclass=ABCMeta):

    @abstractmethod
    def parse(self, input: str) -> T:
        pass


class TokenBasedAlgorithm(BaseAlgorithm[T]):

    def get_tokens(self, input: str) -> TokenSeq:
        return TokenSeq.from_string(input)

    def parse(self, input: str) -> T:  # TODO: may take TokenSeq?
        tokens = self.get_tokens(input)
        return self.parse_by_tokens(tokens)

    @abstractmethod
    def parse_by_tokens(self, token_seq: TokenSeq) -> T:
        pass


class BaseSelector(Generic[T], metaclass=ABCMeta):

    @abstractmethod
    def select(self, inputs: T) -> str:
        pass


class NewSequenceResult(BaseResult):
    seq: TokenSeq

    def __init__(self, seq: TokenSeq):
        self.seq = seq
