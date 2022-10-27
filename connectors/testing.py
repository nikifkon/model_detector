from typing import Generator, NamedTuple, Optional, Iterable
from connectors.base import BaseConnector
from connectors.models import SeriesModel, ManufacturerModel, ModelModel
from tokens import TokenSeq


class TestingConnector(BaseConnector):

    def connect(self):
        pass

    def read_and_update_data_tables(self, columns: tuple[str], where: str) -> Generator[NamedTuple, dict, None]:
        pass

    def read(self, cursor, table, columns: Iterable[str], where: str = '', limit=18446744073709551615):
        pass

    def update(self, cursor, table: str, id: int, data: dict):
        pass

    def check_model_existence(self, model: TokenSeq) -> Optional[ModelModel]:
        pass

    def check_manufacturer_existence(self, manufacturer: TokenSeq) -> Optional[ManufacturerModel]:
        pass

    def check_series_existence(self, manufacturer: TokenSeq) -> Optional[SeriesModel]:
        pass

    def check_is_essence_banned(self, essence: TokenSeq) -> bool:
        pass
