import logging
import os
from typing import Generator, NamedTuple, Optional, Iterable

import redis
from mysql import connector

from connectors.base import BaseConnector
from connectors.models import ManufacturerModel, ModelModel, SeriesModel, ManufacturerStatus, MANUFACTURER_PREFIX, SERIES_PREFIX, SeriesStatus
from tokens import TokenSeq, dump_string


logger = logging.getLogger(__name__)


def join_update_params(data: dict) -> str:
    return ",\n".join([f"{key} = %s" for key in data.keys()])


class ProductionConnector(BaseConnector):
    def __init__(self, force_fetch=False):
        self.data_tables = {
            'promyshlennoe_oborudovanie_pulscen': 'P',
            'promyshlennoe_oborudovanie_satom': 'S',
            'promyshlennoe_oborudovanie_avito': 'A'
        }
        self.r = redis.Redis()
        if force_fetch:
            with self.r.pipeline() as pipe:
                with self.connect() as connection:
                    cur = connection.cursor()
                    self._clear_redis(pipe)
                    self._manufacturers_to_redis(pipe, cur)
                    self._series_to_redis(pipe, cur)
                    self._models_to_redis(pipe, cur)
                pipe.execute()
        super().__init__()

    def _clear_redis(self, pipe: redis.client.Pipeline):
        logger.debug("FLUSHDB...")
        pipe.flushdb()
        pipe.execute()
        logger.debug("FLUSHDB FINISHED")

    def _manufacturers_to_redis(self, pipe: redis.client.Pipeline, cursor):
        table = 'manufacturers_list'
        logger.debug(f'Collecting manufacturers from {table}...')

        wait_for_master = {}  # master_id -> slave_key
        for row_id, manufacturer, synonym_to, status in self.read(
                cursor,
                table=table,
                columns=('id', 'manufacturer', 'synonym_to', 'status'),
                where=f'WHERE status = "{ManufacturerStatus.VERIFIED.value}"',
                order='ORDER BY synonym_to DESC'):
            key = MANUFACTURER_PREFIX + dump_string(manufacturer)
            pipe.hset(key, mapping={
                "id": row_id,
                "normal_form": manufacturer,
                "status": ManufacturerStatus.VERIFIED.value
            })
            if synonym_to:
                wait_for_master[synonym_to] = key
            if row_id in wait_for_master:
                pipe.hset(wait_for_master[row_id], mapping={
                    "synonym_to": key
                })
        logger.debug(f'Collecting manufacturers from {table} FINISHED')

    def _series_to_redis(self, pipe: redis.client.Pipeline, cursor):
        table = 'series_list'
        logger.debug(f'Collecting series from {table}...')
        searched_manufacturers = {}  # manufacturer_id to series_keys
        for row_id, series, manufacturer, status in self.read(
                cursor,
                table=table,
                columns=('id', 'series', 'manufacturer', 'status'),
                where=f'WHERE status = "{ManufacturerStatus.VERIFIED.value}"'):
            key = SERIES_PREFIX + dump_string(series)
            pipe.hset(key, mapping={
                "id": row_id,
                "normal_form": series,
                "status": ManufacturerStatus.VERIFIED.value
            })
            if manufacturer:
                if manufacturer not in searched_manufacturers:
                    searched_manufacturers[manufacturer] = []
                searched_manufacturers[manufacturer].append(key)

        for row_id, manufacturer in self.read(
                cursor,
                table='manufacturers_list',
                columns=('id', 'manufacturer')):
            if row_id in searched_manufacturers:
                for series_key in searched_manufacturers[row_id]:
                    pipe.rpush(series_key + ':manufacturers', dump_string(manufacturer))
                searched_manufacturers.pop(row_id)
        logger.debug(f'{len(searched_manufacturers.keys())} manuf not found')

        logger.debug(f'Collecting series from {table} FINISHED')

    def _models_to_redis(self, pipe: redis.client.Pipeline, cursor):
        pass  # db not exists

    def connect(self):
        from dotenv import load_dotenv
        load_dotenv()
        return connector.connect(
            host=os.environ.get('MYSQL_HOST'),
            port=os.environ.get('MYSQL_PORT'),
            user=os.environ.get('MYSQL_USER'),
            password=os.environ.get('MYSQL_PASSWORD'),
            database=os.environ.get('MYSQL_DATABASE')
        )

    def update(self, cursor, table: str, id: int, data: dict):
        query = f"""
UPDATE {table}
SET
{join_update_params(data)}
WHERE id = %s
        """
        cursor.execute(query, (*data.values(), id))

    def read(self, cursor, table, columns: Iterable[str], where: str = '', limit=18446744073709551615, order: str = '', offset=0):
        assert 'id' in columns
        offset = offset
        cursor.execute(f"""
SELECT {",".join(columns)}
FROM {table}
{where}
{order}
LIMIT {limit}
OFFSET {offset};
        """)
        for row in cursor.fetchall():
            yield row

    def read_and_update_data_tables(self, columns: Iterable[str], where: str = '', limit=18446744073709551615, offset=0) -> \
            Generator[NamedTuple, dict, None]:
        with self.connect() as connection:
            cur = connection.cursor()

            for table, prefix in self.data_tables.items():
                for row in self.read(cur, table, columns, where, limit, offset=offset):
                    (id, *other) = row
                    data = yield other
                    if data:
                        try:
                            self.update(cur, table, id, data)
                        except:  # noqa: E722
                            print(id)  # print offset in next run
                            break
                        yield
            connection.commit()

    def encode_table(self, id: int, table: str) -> str:
        return f'{self.data_tables[table]}{id}'

    def decode_table(self, id: str) -> tuple[int, str]:
        return int(id[1:]), list(self.data_tables.keys())[list(self.data_tables.values()).index(id[0])]

    def check_manufacturer_existence(self, suspect: TokenSeq) -> Optional[ManufacturerModel]:
        key = MANUFACTURER_PREFIX + suspect.dump_seq()
        return self._get_manufacturer(key)

    def _get_manufacturer(self, key: str) -> Optional[ManufacturerModel]:
        if self.r.exists(key):
            bin_data = self.r.hgetall(key)
            data = {
                'normal_form': bin_data[b'normal_form'].decode('utf-8'),
                'status': ManufacturerStatus(bin_data[b'status'].decode('utf-8'))
            }
            return ManufacturerModel(**data)

    def check_model_existence(self, suspect: TokenSeq) -> Optional[ModelModel]:
        pass  # TODO

    def check_series_existence(self, suspect: TokenSeq) -> Optional[SeriesModel]:
        key = SERIES_PREFIX + suspect.dump_seq()
        if self.r.exists(key):
            bin_data = self.r.hgetall(key)
            manufacturers = [manufacturer.decode('utf-8') for manufacturer in self.r.lrange(key + ':manufacturers', 0, -1)]

            data = {
                'normal_form': bin_data[b'normal_form'].decode('utf-8'),
                'status': SeriesStatus(bin_data[b'status'].decode('utf-8')),
                'manufacturers': [self._get_manufacturer(manuf) for manuf in manufacturers]
            }
            return SeriesModel(**data)

    def check_is_essence_banned(self, essence: TokenSeq) -> bool:
        return False
