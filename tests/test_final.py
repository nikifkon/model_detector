import pytest
from typing import Callable, Iterator, NamedTuple, Optional

from algorithms.final import Final
from algorithms.find_models import FindModels
from connectors.models import ManufacturerStatus, ModelModel, ManufacturerModel, ManufacturerMethod
from connectors.base import BaseConnector

from tokens import TokenSeq


hod = ManufacturerMethod
FS = ManufacturerStatus
MM = ModelModel
FM = ManufacturerModel


class MockConnector(BaseConnector):
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
        }
    }

    def connect(self):
        pass

    def update(self, cursor, id: str, data: dict):
        pass

    def read_and_update(self, columns: tuple[str], where: str = '', limit=18446744073709551615) -> Iterator[tuple[NamedTuple, Callable[[int, dict], None]]]:
        pass

    def read(self, columns: tuple[str], where: str = '', limit=18446744073709551615) -> NamedTuple:
        pass

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
        model = FM(details['normal_form'], details['status'])
        return model
        # TODO synonims

    def dump_seq(self, seq: TokenSeq):
        return ';'.join(map(lambda x: str(x).lower(), seq.iter_by_values()))


def run_test(input, essence, manufacturer_model, model_model, method):
    res = Final(MockConnector()).parse(input)
    assert res.essence == essence
    assert res.manufacturer_model == manufacturer_model
    assert res.model_model == model_model
    assert res.method == method


@pytest.mark.parametrize('input, essence, manufacturer_model, model_model, method', [
    ('Газовая сварочная смесь К-25 Аргон+Углекислота 40л',
     'Смесь', None, MM('К-25'), None),
    ('Парогенератор Tefal Pro Express Protect GV9230E0',
     'Парогенератор', FM('Tefal', FS.VERIFIED), MM('Pro Express Protect GV9230E0'), hod.BY_NAME_CLEAR),
    ('Клапан обр лат пов Ду20 Ру16 м/м д/лат Giacomini N6Y004',
     'Клапан', FM('Giacomini', FS.FROM_SATOM), MM('N6Y004', series='ГНОМ'), hod.BY_NAME_CLEAR),
    ('Сварочный полуавтомат TSS top MIG/MMA-160 DG',
     'Полуавтомат', FM('TSS', FS.VERIFIED), MM('top MIG/MMA-160 DG'), hod.BY_NAME_CLEAR),
    ('Ленточная пилорама "КЕДР-Гибрид" (11 кВт)',
     'Полуавтомат', FM('КЕДР', FS.VERIFIED), MM('Гибрид'), hod.BY_NAME_CLEAR),
    ('Высоколегированная сварочная проволока 1.2 мм Св-05Х19Н9Ф3С2 ГОСТ 2246-70',
     'Проволока', None, MM('Св-05Х19Н9Ф3С2'), None),
])
def test_by_name_clear__simple(input: str, essence: str, manufacturer_model: FM, model_model: MM, method: ManufacturerMethod):
    run_test(input, essence, manufacturer_model, model_model, method)


# TODO test data
@pytest.mark.parametrize('input, essence, manufacturer_model, model_model, method', [
    ('Циркуляционный насос Wilo Yonos PICO 25/1-6-130 4164018',
     'насос', FM('Wilo', FS.VERIFIED), MM('Yonos PICO 25/1-6-130'), hod.BY_NAME_CLEAR),
])
def test_by_name_clear__with_article(input: str, essence: str, manufacturer_model: FM, model_model: MM, method: ManufacturerMethod):
    run_test(input, essence, manufacturer_model, model_model, method)


@pytest.mark.parametrize('input, essence, manufacturer_model, model_model, method', [
    ('Дренажный насос ГНОМ 16-16 Д 220В (Ливны, с поплавком)',
     'насос', FM('ливгидромаш', FS.VERIFIED), MM('ГНОМ 16-16 Д', series='ГНОМ'), hod.BY_SERIES),
])
def test_by_series__simple(input: str, essence: str, manufacturer_model: FM, model_model: MM, method: ManufacturerMethod):
    run_test(input, essence, manufacturer_model, model_model, method)


@pytest.mark.parametrize('input, essence, manufacturer_model, model_model, method', [
    ('PIUSI SPA BP 3000 12V - Роторный лопастной электронасос для ДТ, 50 л/мин (безрезьб. Б/эл. компл.)',
     'электронасос', FM('Piusi', FS.VERIFIED), MM('Piusi BP 3000'), hod.BY_NAME_CLEAR),
])
def test_by_name__manuf_synonym(input: str, essence: str, manufacturer_model: FM, model_model: MM, method: ManufacturerMethod):
    run_test(input, essence, manufacturer_model, model_model, method)


@pytest.mark.parametrize('input, essence, manufacturer_model, model_model, method', [
    ('Поршневой компрессор Fiac AB 500 - 858/16',
     'компрессор', None, MM('Fiac AB 500 - 858'), None),
    ('Поршневой компрессор aircast сб4/ф-500. LT100/10-11,0',
     'компрессор', FM('Remeza', FS.VERIFIED), MM('AirCast сб4/ф-500', series='AirCast'), hod.BY_SERIES),
])
def test_by_name__model_synonym(input: str, essence: str, manufacturer_model: FM, model_model: MM, method: ManufacturerMethod):
    run_test(input, essence, manufacturer_model, model_model, method)


@pytest.mark.parametrize('input, essence, manufacturer_model, model_model, method', [
    ('Подшипник ступицы 4030042SX',
     'Подшипник', FM('Stellox', FS.VERIFIED), MM('4030042SX'), hod.BY_ANALOGY),
])
def test_by_analogy(input: str, essence: str, manufacturer_model: FM, model_model: MM, method: ManufacturerMethod):
    run_test(input, essence, manufacturer_model, model_model, method)


@pytest.mark.parametrize('input, essence, manufacturer_model, model_model, method', [
    ('Ленточная пилорама Тайга Астрон Алтай Кедр в налич',
     'пилорама', FM(FS.MULTY, FS.MULTY), MM(' & '.join(['Тайга', 'Астрон', 'Алтай', 'Кедр'])), hod.BY_NAME_CLEAR)
])
def test_multi(input: str, essence: str, manufacturer_model: FM, model_model: MM, method: ManufacturerMethod):
    run_test(input, essence, manufacturer_model, model_model, method)


@pytest.mark.parametrize('input', [
    'Fiac AB 500-858',
    'Fiac;AB 500 858',
    'fiac aB 500×858',
    'asdf fiac aB 500×858 ff',
])
def test_find_model(input: str):
    conn = MockConnector()
    is_model_exists = conn.check_model_existence
    fm = FindModels(is_model_exists)
    res = fm.parse(input)
    assert res.model == MM('Fiac AB 500-858', essence='компрессор')


def test_by_verified_model():
    run_test('a asdfj adslkfj as Fiac AB 500 858 фывло', 'компрессор', None, MM('Fiac AB 500-858', essence='компрессор'), hod.BY_VERIFIED_MODEL)
