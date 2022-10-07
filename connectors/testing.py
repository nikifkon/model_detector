from typing import Callable, Generator, NamedTuple
from connectors.base import BaseConnector


class TestingConnector(BaseConnector):
    def read_and_update(columns: tuple[str], where: str) -> Generator[NamedTuple, Callable[[dict], None]]:
        pass
