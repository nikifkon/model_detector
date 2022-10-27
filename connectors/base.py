from abc import ABCMeta, abstractmethod
from typing import NamedTuple, Optional, Iterable, Generator

from connectors.models import ManufacturerModel, ModelModel, SeriesModel
from tokens import TokenSeq


class BaseConnector(metaclass=ABCMeta):
    def __init__(self):
        pass

    # interface for infrastructure
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def read_and_update_data_tables(self, columns: tuple[str], where: str) -> Generator[NamedTuple, dict, None]:
        pass

    @abstractmethod
    def read(self, cursor, table, columns: Iterable[str], where: str = '', limit=18446744073709551615):
        pass

    @abstractmethod
    def update(self, cursor, table: str, id: int, data: dict):
        pass

    # interface for algorithm:
    @abstractmethod
    def check_model_existence(self, model: TokenSeq) -> Optional[ModelModel]:
        pass

    @abstractmethod
    def check_manufacturer_existence(self, manufacturer: TokenSeq) -> Optional[ManufacturerModel]:
        pass

    @abstractmethod
    def check_series_existence(self, manufacturer: TokenSeq) -> Optional[SeriesModel]:
        pass

    @abstractmethod
    def check_is_essence_banned(self, essence: TokenSeq) -> bool:
        pass
