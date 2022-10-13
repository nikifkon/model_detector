from abc import ABCMeta, abstractmethod
from typing import Iterator, Callable, NamedTuple, Optional

from connectors.models import ManufacturerModel, ModelModel
from tokens import TokenSeq


class BaseConnector(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def read_and_update(columns: tuple[str], where: str) -> Iterator[tuple[NamedTuple, Callable[[dict], None]]]:
        pass

    @abstractmethod
    def read(self, columns: tuple[str], where: str = None):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def check_model_existence(self, model: TokenSeq) -> Optional[ModelModel]:
        pass

    @abstractmethod
    def check_manufacturer_existence(self, manufacturer: TokenSeq) -> Optional[ManufacturerModel]:
        pass
