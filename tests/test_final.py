import pytest
from typing import Optional

from algorithms.final import Final
from algorithms.find_models import FindModels
from algorithms.find_manufacturer import FindManufacturers, FindManufacturersResult
from algorithms.find_series import FindSeries
from algorithms.defaults import DefaultAlgorithm
from connectors.models import ManufacturerStatus, ModelModel, ManufacturerModel, ManufacturerMethod, SeriesModel, \
    SeriesStatus

hod = ManufacturerMethod
FS = ManufacturerStatus
MM = ModelModel
FM = ManufacturerModel


def run_test(connector, input: str, model_model: ModelModel, method: hod):
    res = Final(connector).parse(input)
    assert res.model_model == model_model
    assert res.method == method


@pytest.mark.parametrize('input, model_model, method', [
    ('Газовая сварочная смесь К-25 Аргон+Углекислота 40л',
     MM('К-25', essence='Смесь'), ManufacturerMethod.MISSED),
    ('Парогенератор Tefal Pro Express Protect GV9230E0',
     MM('Pro Express Protect GV9230E0', manufacturer=FM('Tefal', FS.VERIFIED), essence='Парогенератор'),
     hod.BY_NAME_CLEAR),
    ('Клапан обр лат пов Ду20 Ру16 м/м д/лат Giacomini N6Y004',
     MM('N6Y004', manufacturer=(manuf := FM('Giacomini', FS.VERIFIED)), essence='Клапан'), hod.BY_NAME_CLEAR),
    # ('Сварочный полуавтомат TSS top MIG/MMA-160 DG',
    #  'Полуавтомат', FM('TSS', FS.VERIFIED), MM('top MIG/MMA-160 DG'), hod.BY_NAME_CLEAR),
    ('Ленточная пилорама "КЕДР-Гибрид" (11 кВт)',
     MM('Гибрид', essence='Полуавтомат', manufacturer=FM('КЕДР', FS.VERIFIED)), hod.BY_NAME_CLEAR),
    ('Высоколегированная сварочная проволока 1.2 мм Св-05Х19Н9Ф3С2 ГОСТ 2246-70',
     MM('Св-05Х19Н9Ф3С2', essence='Проволока'), ManufacturerMethod.MISSED),
])
def test_by_name_clear__simple(connector, input: str, model_model: MM, method: ManufacturerMethod):
    run_test(connector, input, model_model, method)


@pytest.mark.parametrize('input, model_model, method', [
    ('Циркуляционный насос Wilo Yonos PICO 25/1-6-130 4164018',
     MM('Yonos PICO 25/1-6-130', manufacturer=FM('Wilo', FS.VERIFIED), essence='Насос'), hod.BY_NAME_CLEAR),
])
def test_by_name_clear__with_article(connector, input: str, model_model: MM, method: ManufacturerMethod):
    run_test(connector, input, model_model, method)


@pytest.mark.parametrize('input, model_model, method', [
    ('Дренажный насос ГНОМ 16-16 Д 220В (Ливны, с поплавком)',
     MM('ГНОМ 16-16 Д', manuf := FM('Ливгидромаш', FS.VERIFIED), essence='Насос', series=SeriesModel('Гном', manuf)),
     hod.BY_SERIES),
])
def test_by_series__simple(connector, input: str, model_model: ModelModel, method: ManufacturerMethod):
    run_test(connector, input, model_model, method)


@pytest.mark.parametrize('input, model_model, method', [
    ('PIUSI BP 3000 12V - Роторный лопастной электронасос для ДТ, 50 л/мин (безрезьб. Б/эл. компл.)',
     MM('BP 3000', manufacturer=FM('Piusi', FS.VERIFIED), essence='Электронасос'), hod.BY_NAME_CLEAR),
    ('Теплообменник пластинчатый паяный Alfa Laval AC 30',
     MM('AC 30', manufacturer=FM('Alfa Laval', FS.VERIFIED), essence='Теплообменник'), hod.BY_NAME_CLEAR),
    ('Теплообменник пластинчатый паяный Alfa Laval AC 30 Alfa Laval',
     MM('AC 30', manufacturer=FM('Alfa Laval', FS.VERIFIED), essence='Теплообменник'), hod.BY_NAME_CLEAR)
])
def test_by_name__manuf_synonym(connector, input: str, model_model: MM, method: ManufacturerMethod):
    run_test(connector, input, model_model, method)


# Failed cuz we use production connector and production database may haven't verified model
@pytest.mark.parametrize('input, model_model, method', [
    ('Поршневой компрессор Fiac AB 500 - 858/16',
     MM('Fiac AB 500 - 858', essence='Компрессор'), None),
    ('Поршневой компрессор aircast сб4/ф-500. LT100/10-11,0',
     MM('AirCast сб4/ф-500', manufacturer=FM('Remeza', FS.VERIFIED), essence='Компрессор', series='AirCast'),
     hod.BY_SERIES),
])
def test_by_name__model_synonym(connector, input: str, model_model: MM, method: ManufacturerMethod):
    run_test(connector, input, model_model, method)


# Failed cuz we use production connector and production database may haven't verified model
@pytest.mark.parametrize('input, model_model, method', [
    ('Подшипник ступицы 4030042SX',
     MM('4030042SX', manufacturer=FM('Stellox', FS.VERIFIED), essence='Подшипник'), hod.BY_ANALOGY),
])
def test_by_analogy(connector, input: str, model_model: MM, method: ManufacturerMethod):
    run_test(connector, input, model_model, method)


@pytest.mark.parametrize('input, model_model, method', [
    ('Ленточная пилорама Тайга Астрон Алтай Кедр в налич',
     MM(' & '.join(['Алтай', 'Астрон', 'Кедр', 'Тайга'])), hod.MULTY)
])
def test_multy(connector, input: str, model_model: MM, method: ManufacturerMethod):
    run_test(connector, input, model_model, method)


# Failed cuz we use production connector and production database may haven't verified model
@pytest.mark.parametrize('input', [
    'Fiac AB 500-858',
    'Fiac;AB 500 858',
    'fiac aB 500×858',
    'asdf fiac aB 500×858 ff',
])
def test_find_model(connector, input: str):
    fm = FindModels(connector.check_model_existence)
    res = fm.parse(input)
    assert res.model == MM('Fiac AB 500-858', essence='компрессор')


@pytest.mark.parametrize('input, expected_res', {
    ('Парогенератор Tefal Pro Express Protect GV9230E0',
     FindManufacturersResult(None, frozenset([FM('Tefal', FS.VERIFIED)]), hod.BY_NAME_CLEAR)),
    ('Сварочный полуавтомат TSS top MIG/MMA-160 DG',
     FindManufacturersResult(None, frozenset([FM('TSS', FS.VERIFIED)]), hod.BY_NAME_CLEAR)),
    ('Ленточная пилорама Тайга Астрон Алтай Кедр в налич', FindManufacturersResult(None, frozenset(
        [FM('Тайга', FS.VERIFIED), FM('Кедр', FS.VERIFIED), FM('Астрон', FS.VERIFIED), FM('Алтай', FS.VERIFIED)]), hod.MULTY)),
    ('Дренажный насос ГНОМ 16-16 Д 220В (Ливны, с поплавком)',
     FindManufacturersResult(None, frozenset([manuf := FM('Ливгидромаш', FS.VERIFIED)]), hod.BY_SERIES, SeriesModel('Гном', manufacturer=manuf, status=SeriesStatus.VERIFIED))),
    ('Wilo Tefal-100',
     FindManufacturersResult(None, frozenset([manuf := FM('Wilo', FS.VERIFIED)]), hod.BY_NAME_CLEAR)),
    ('Горелка ABICOR BINZEL ABITIG GRIP 17 F, 8 м',
     FindManufacturersResult(None, frozenset([manuf := FM('Abicor Binzel', FS.VERIFIED)]), hod.BY_NAME_CLEAR)),
    ('Электрический резьбонарезной станок SUPER-EGO HEAVY 2"',
     FindManufacturersResult(None, frozenset([manuf := FM('Super-Ego', FS.VERIFIED)]), hod.BY_NAME_CLEAR)),
})
def test_find_manufacturer(connector, input: str, expected_res: FindManufacturersResult):
    fm = FindManufacturers(connector.check_manufacturer_existence, connector.check_series_existence)
    res = fm.parse_by_tokens(DefaultAlgorithm().parse(input).seq)
    assert res.manufacturers == expected_res.manufacturers
    assert res.method == expected_res.method
    assert res.series == expected_res.series


@pytest.mark.parametrize('input, series', [
    ('Дренажный насос ГНОМ 16-16 Д 220В (Ливны, с поплавком)',
     SeriesModel('Гном', status=SeriesStatus.VERIFIED, manufacturer=FM('Ливгидромаш', FS.VERIFIED))),
    ('Ленточная пилорама Тайга Астрон Алтай Кедр в налич', None),
])
def test_find_series(connector, input: str, series: Optional[SeriesModel]):
    fm = FindSeries(connector.check_series_existence)
    res = fm.parse(input)
    assert res.series == series
