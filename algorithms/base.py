from abc import ABCMeta, abstractclassmethod, abstractmethod
from dataclasses import dataclass
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


@dataclass(eq=True, frozen=True)
class BaseResult(Generic[TLogEntry], metaclass=ABCMeta):
    logs: TLogEntry


TResult = TypeVar('TResult', bound=BaseResult)


class BaseAlgorithm(Generic[TResult], metaclass=ABCMeta):

    @abstractmethod
    def parse(self, input: str) -> TResult:
        pass


class TokenBasedAlgorithm(BaseAlgorithm[TResult]):

    def get_tokens(self, input: str) -> TokenSeq:
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
class NewSequenceResult(Generic[TLogEntry], BaseResult[TLogEntry]):
    seq: TokenSeq

    # def __init__(self, seq: TokenSeq = None, **kwags):
    #     self.seq = seq
    #     super().__init__(**kwags)


class EmptyLog(BaseLogEntry):
    def dump_data(self) -> str:
        return '{}'

    @classmethod
    def load_data(cls, dump: str) -> Self:
        return cls()
