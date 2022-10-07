import pytest

from algorithms.final import Final
from connectors.models import ManufacturerStatus, ModelModel, ManufacturerModel, ManufacturerMethod
from connectors.base import BaseConnector

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
        'Fiac AB 500-858': {
            'status': ...,
            'normal_form': 'Fiac AB 500-858',
            'manufacturer': '',
            'essence': 'компрессор'
        }
    }

    def connect(self):
        pass

    def check_model_existence(self, model: str, essence: str = None, manufacturer: str = None) -> tuple[bool, MM]:
        if model not in self.registered_models:
            return False, None
        details = self.registered_models[model]
        return True, MM(details['normal_form'])
        # TODO

    def check_manufacturer_existence(self, manufacturer: str) -> tuple[bool, FM]:
        if manufacturer not in self.registered_manufacturers:
            return False, None
        details = self.registered_manufacturers[manufacturer]
        if details['status'] == FS.BANNED:
            return False, None
        model = FM(details['normal_form'], details['status'])
        return True, model
        # TODO synonims


def run_test(input, essence, manufacturer_model, model_model):
    res = Final().parse(input)
    assert res.essence == essence
    assert res.manufacturer_model == manufacturer_model
    assert res.model_model == model_model


@pytest.mark.parametrize('input, essence, manufacturer_model, model_model', [
    ('Газовая сварочная смесь К-25 Аргон+Углекислота 40л',
     'Смесь', None, MM('К-25')),
    ('Парогенератор Tefal Pro Express Protect GV9230E0',
     'Парогенератор', FM('Tefal', FS.VERIFIED, hod.BY_NAME_CLEAR), MM('Pro Express Protect GV9230E0')),
    ('Клапан обр лат пов Ду20 Ру16 м/м д/лат Giacomini N6Y004',
     'Клапан', FM('Giacomini', FS.FROM_SATOM, hod.BY_NAME_CLEAR), MM('N6Y004', series='ГНОМ')),
    ('Сварочный полуавтомат TSS top MIG/MMA-160 DG',
     'Полуавтомат', FM('TSS', FS.VERIFIED, hod.BY_NAME_CLEAR), MM('top MIG/MMA-160 DG')),
    ('Ленточная пилорама "КЕДР-Гибрид" (11 кВт)',
     'Полуавтомат', FM('КЕДР', FS.VERIFIED, hod.BY_NAME_CLEAR), MM('Гибрид')),
    ('Высоколегированная сварочная проволока 1.2 мм Св-05Х19Н9Ф3С2 ГОСТ 2246-70',
     'Проволока', None, MM('Св-05Х19Н9Ф3С2')),
])
def test_by_name_clear__simple(input: str, essence: str, manufacturer_model: FM, model_model: MM):
    run_test(input, essence, manufacturer_model, model_model)

# TODO test data


@pytest.mark.parametrize('input, essence, manufacturer_model, model_model', [
    ('Циркуляционный насос Wilo Yonos PICO 25/1-6-130 4164018',
     'насос', FM('Wilo', FS.VERIFIED, hod.BY_NAME_CLEAR), MM('Yonos PICO 25/1-6-130')),
])
def test_by_name_clear__with_article(input: str, essence: str, manufacturer_model: FM, model_model: MM):
    run_test(input, essence, manufacturer_model, model_model)


@pytest.mark.parametrize('input, essence, manufacturer_model, model_model', [
    ('Дренажный насос ГНОМ 16-16 Д 220В (Ливны, с поплавком)',
     'насос', FM('ливгидромаш', FS.VERIFIED, hod.BY_SERIES), MM('ГНОМ 16-16 Д', series='ГНОМ')),
])
def test_by_series__simple(input: str, essence: str, manufacturer_model: FM, model_model: MM):
    run_test(input, essence, manufacturer_model, model_model)


@pytest.mark.parametrize('input, essence, manufacturer_model, model_model', [
    ('PIUSI SPA BP 3000 12V - Роторный лопастной электронасос для ДТ, 50 л/мин (безрезьб. Б/эл. компл.)',
     'электронасос', FM('Piusi', FS.VERIFIED, hod.BY_NAME_CLEAR, 'Piusi SpA'), MM('Piusi BP 3000')),
])
def test_by_name__manuf_synonym(input: str, essence: str, manufacturer_model: FM, model_model: MM):
    run_test(input, essence, manufacturer_model, model_model)


@pytest.mark.parametrize('input, essence, manufacturer_model, model_model', [
    ('Поршневой компрессор Fiac AB 500 - 858/16',
     'компрессор', None, MM('Fiac AB 500 - 858', original_model='Fiac AB 500 - 858/16')),
    ('Поршневой компрессор aircast сб4/ф-500. LT100/10-11,0',
     'компрессор', FM('Remeza', FS.VERIFIED, hod.BY_SERIES), MM('AirCast сб4/ф-500', series='AirCast', original_model='AirCast сб4/ф-500. LT100/10-11,0')),
])
def test_by_name__model_synonym(input: str, essence: str, manufacturer_model: FM, model_model: MM):
    run_test(input, essence, manufacturer_model, model_model)


@pytest.mark.parametrize('input, essence, manufacturer_model, model_model', [
    ('Подшипник ступицы 4030042SX',
     'Подшипник', FM('Stellox', FS.VERIFIED, hod.BY_ANALOGY), MM('4030042SX')),
])
def test_by_analogy(input: str, essence: str, manufacturer_model: FM, model_model: MM):
    run_test(input, essence, manufacturer_model, model_model)


@pytest.mark.parametrize('input, essence, manufacturer_model, model_model', [
    ('Ленточная пилорама Тайга Астрон Алтай Кедр в налич',
     'пилорама', FM(FS.MULTY, ' & '.join(FS.VERIFIED), ' & '.join(hod.BY_NAME_CLEAR)), MM(' & '.join(['Тайга', 'Астрон', 'Алтай', 'Кедр']))),
])
def test_multi(input: str, essence: str, manufacturer_model: FM, model_model: MM):
    run_test(input, essence, manufacturer_model, model_model)
