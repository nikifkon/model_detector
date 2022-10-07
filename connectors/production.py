from functools import partial
import os
from typing import Iterator, Callable, NamedTuple

from mysql import connector

from connectors.base import BaseConnector
from connectors.models import ManufacturerModel, ModelModel


def join_update_params(data: dict) -> str:
    return "\n".join([f"{key} = %s," for key in data.keys()])


class ProductionConnector(BaseConnector):
    tables = {
        'promyshlennoe_oborudovanie_pulscen': 'P',
        'promyshlennoe_oborudovanie_satom': 'S',
        'promyshlennoe_oborudovanie_avitoOld': 'A'
    }

    def connect(self):
        from dotenv import load_dotenv
        load_dotenv()
        return connector.connect(
            host=os.environ.get('MYSQL_HOST'),
            port=os.environ.get('MYSQL_PORT'),
            user=os.environ.get('MYSQL_USER'),
            password=os.environ.get('MYSQL_PASSWORD'),
            database='equip'
        )

    def update(self, cursor, id: str, data: dict):
        id, table = self.decode_table(id)
        query = f"""
UPDATE {table}
SET
{join_update_params(data)}
WHERE id = %s
        """
        cursor.execute(query, (*data.values(), id))

    def read_and_update(self, columns: tuple[str], where: str = '', limit=18446744073709551615) -> Iterator[tuple[NamedTuple, Callable[[int, dict], None]]]:
        assert 'id' in columns
        offset = 0
        with self.connect() as connection:
            cur = connection.cursor()

            counter = 0
            for table, prefix in self.tables.items():
                cur.execute(f"""
SELECT {",".join(columns)}
FROM equip.{table}
{where if where else ""}
LIMIT {limit}
OFFSET {offset};
                """)
                while row := cur.fetchone():
                    (id, *other) = row
                    counter += 1
                    if counter % 50_000 == 0:
                        print(counter)
                    yield (self.encode_table(id, table), *other), partial(self.update(cur))
            connection.commit()

    def encode_table(self, id: int, table: str) -> str:
        return f'{self.tables[table]}{id}'

    def decode_table(self, id: str) -> tuple[int, str]:
        return int(id[1:]), list(self.tables.keys())[list(self.tables.values()).index(id[0])]

    def read(self, columns: tuple[str], where: str = '', limit=18446744073709551615) -> NamedTuple:
        assert 'id' in columns
        offset = 0
        with self.connect() as connection:
            cur = connection.cursor()

            counter = 0
            for table, prefix in self.tables.items():
                cur.execute(f"""
SELECT {",".join(columns)}
FROM equip.{table}
{where if where else ""}
LIMIT {limit}
OFFSET {offset};
                """)
                while row := cur.fetchone():
                    (id, *other) = row
                    counter += 1
                    if counter % 50_000 == 0:
                        print(counter)
                    yield self.encode_table(id, table), *other

    def check_manufacturer_existence(self, manufacturer: str) -> tuple[bool, ManufacturerModel]:
        return super().check_manufacturer_existence(manufacturer)

    def check_model_existence(self, model: str, essence: str = None, manufacturer: str = None) -> tuple[bool, ModelModel]:
        return super().check_model_existence(model, essence, manufacturer)
