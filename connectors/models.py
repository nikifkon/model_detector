class ManufacturerStatus:
    VERIFIED = "VERIFIED"
    FROM_PULSCEN = "FROM_PULSCEN"
    FROM_SATOM = "FROM_SATOM"
    MANUAL = "MANUAL"
    BY_STATISTIC = "BY_STATISTIC"
    BANNED = "BANNED"
    MULTY = "MULTY"


class ManufacturerMethod:
    FROM_DATA = "FROM_DATA"
    BY_NAME_CLEAR = "BY_NAME_CLEAR"
    BY_SERIES = "BY_SERIES"
    BY_NAME_DRY = "BY_NAME_DRY"
    BY_ANALOGY = "BY_ANALOGY"

# производитель из данных
#   не забанен -> FROM_DATA, X (может быть новый)
#   забанен -> continue
# нашли в загаловке 1го незабаннего производителя
#   BY_NAME, X
# нашли 2 незабанненых производителей (причем не синонимов)
#   может 2й это серия?
#       BY_NAME, X
#   manuf=MULTI
# иначе
#   ищем серии
#       если у серии только один производитель
#           BY_SERIES, X
#       несколько
#           ТУДУ
#   иначе находим по аналогии среди одинаковый essence
#       BY_ANALOGY, X
#   иначе
#   MISSED, MISSED


class ManufacturerModel:
    def __init__(self, normal_form: str, status: str, method: str, original_manufacturer: 'ManufacturerModel' = None):
        self.normal_form = normal_form
        self.status = status
        self.method = method
        self.original_manufacturer = original_manufacturer
        assert status != ''
        assert normal_form != ''
        assert method != ''
        assert status is not None
        assert normal_form is not None
        assert method is not None


class ModelModel:
    def __init__(self, normal_form: str, series: str = None, original_model: 'ModelModel' = None):
        self.normal_form = normal_form
        self.original_model = original_model
        self.series = series
        assert normal_form != ''
        assert normal_form is not None
