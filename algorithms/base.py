from abc import ABCMeta, abstractclassmethod, abstractmethod
from typing import Generic, TypeVar
from typing_extensions import Self

from tokens import TokenSeq


class BaseLogEntry():
    @abstractmethod
    def dump_data(self) -> str:
        pass

    @abstractclassmethod
    def load_data(cls, dump: str) -> Self:
        pass


TLogEntry = TypeVar('TLogEntry', bound=BaseLogEntry)


class BaseResult(Generic[TLogEntry], metaclass=ABCMeta):
    logs: TLogEntry = None

    def __init__(self):
        pass


TResult = TypeVar('TResult', bound=BaseResult)


class BaseAlgorithm(Generic[TResult], metaclass=ABCMeta):

    @abstractmethod
    def parse(self, input: str) -> TResult:
        pass


class TokenBasedAlgorithm(BaseAlgorithm[TResult]):

    def get_tokens(self, input: str) -> TokenSeq:
        return TokenSeq.from_string(input)

    def parse(self, input: str) -> TResult:  # TODO: may take TokenSeq?
        tokens = self.get_tokens(input)
        return self.parse_by_tokens(tokens)

    @abstractmethod
    def parse_by_tokens(self, token_seq: TokenSeq) -> TResult:
        pass


class BaseSelector(Generic[TResult], metaclass=ABCMeta):

    @abstractmethod
    def select(self, inputs: TResult) -> str:
        pass


class NewSequenceResult(Generic[TLogEntry], BaseResult[TLogEntry]):
    seq: TokenSeq

    def __init__(self, seq: TokenSeq = None, **kwags):
        self.seq = seq
        super().__init__(**kwags)
