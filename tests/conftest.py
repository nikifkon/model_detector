from typing import NamedTuple, Optional, Iterable, Generator

import pytest

from connectors.models import ManufacturerStatus, ModelModel, ManufacturerModel, ManufacturerMethod, SeriesModel
from connectors.production import ProductionConnector
from tokens import TokenSeq

hod = ManufacturerMethod
FS = ManufacturerStatus
MM = ModelModel
FM = ManufacturerModel


@pytest.fixture(scope="session")
def connector():
    return ProductionConnector()


class MockConnector(ProductionConnector):
    def connect(self):
        pass

    def read_and_update_data_tables(self, columns: tuple[str], where: str) -> Generator[NamedTuple, dict, None]:
        pass

    def read(self, cursor, table, columns: Iterable[str], where: str = '', limit=18446744073709551615):
        pass

    def update(self, cursor, table: str, id: int, data: dict):
        pass

    registered_manufacturers = {
        'tefal': {
            'status': FS.VERIFIED,
            'normal_form': 'Tefal',
            'synonym_to': None
        },
        'giacomini': {
            'status': FS.VERIFIED,
            'normal_form': 'Giacomini',
            'synonym_to': None
        },
        'wilo': {
            'status': FS.VERIFIED,
            'normal_form': 'Wilo',
            'synonym_to': None
        },
        'ливгидромаш': {
            'status': FS.VERIFIED,
            'normal_form': 'Ливгидромаш',
            'synonym_to': None
        },
        'remeza': {
            'status': FS.VERIFIED,
            'normal_form': 'Remeza',
            'synonym_to': None
        },
        'piusi': {
            'status': FS.VERIFIED,
            'normal_form': 'Piusi',
            'synonym_to': None
        },
        'тайга': {
            'status': FS.VERIFIED,
            'normal_form': 'Тайга',
            'synonym_to': None
        },
        'астрон': {
            'status': FS.VERIFIED,
            'normal_form': 'Астрон',
            'synonym_to': None
        },
        'алтай': {
            'status': FS.VERIFIED,
            'normal_form': 'Алтай',
            'synonym_to': None
        },
        'stellox': {
            'status': FS.VERIFIED,
            'normal_form': 'Stellox',
            'synonym_to': None
        }
    }

    registered_series = {
        'гном': {
            'manufacturer': 'ливгидромаш',
            'normal_form': 'ГНОМ'
        },
        'aircast': {
            'manufacturer': 'remeza',
            'normal_form': 'AirCast'
        },
    }

    registered_models = {
        'fiac;ab;500;858': {
            'normal_form': 'Fiac AB 500-858',
            'manufacturer': None,
            'essence': 'компрессор'
        },
        '4030042sx': {
            'normal_form': '4030042SX',
            'manufacturer': 'stellox',
            'essence': 'Подшипник'
        }
    }

    def check_model_existence(self, model: TokenSeq) -> Optional[MM]:
        key = self.dump_seq(model)
        if key not in self.registered_models:
            return None
        details = self.registered_models[key]

        manuf = None
        if 'manufacturer' in details and details['manufacturer'] is not None:
            manuf = self.check_manufacturer_existence(TokenSeq.from_string(details['manufacturer']))
            assert manuf
        return MM(details['normal_form'], essence=details['essence'], manufacturer=manuf)

    def check_manufacturer_existence(self, manufacturer: TokenSeq) -> Optional[FM]:
        key = self.dump_seq(manufacturer)
        if key not in self.registered_manufacturers:
            return None
        details = self.registered_manufacturers[key]
        if details['status'] == FS.BANNED:
            return None
        return FM(details['normal_form'], details['status'])
        # TODO synonims

    def check_series_existence(self, series: TokenSeq) -> Optional[SeriesModel]:
        key = self.dump_seq(series)
        if key not in self.registered_series:
            return None
        details = self.registered_series[key]
        if 'manufacturer' in details and details['manufacturer'] is not None:
            manuf = self.check_manufacturer_existence(TokenSeq.from_string(details['manufacturer']))
            assert manuf
        return SeriesModel(details['normal_form'], manuf)

    def check_is_essence_banned(self, esssnce: TokenSeq) -> bool:
        return False

    def dump_seq(self, seq: TokenSeq):
        return ';'.join(map(lambda x: str(x).lower(), seq.iter_by_values()))
