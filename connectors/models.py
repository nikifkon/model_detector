from dataclasses import dataclass
from enum import Enum


class ManufacturerStatus(Enum):
    VERIFIED = "VERIFIED"
    FROM_PULSCEN = "FROM_PULSCEN"
    FROM_SATOM = "FROM_SATOM"
    MANUAL = "MANUAL"
    BY_STATISTIC = "BY_STATISTIC"
    BANNED = "BANNED"
    MULTY = "MULTY"


class ManufacturerMethod(Enum):
    FROM_DATA = "FROM_DATA"
    BY_NAME_CLEAR = "BY_NAME_CLEAR"
    BY_SERIES = "BY_SERIES"
    BY_NAME_DRY = "BY_NAME_DRY"
    BY_ANALOGY = "BY_ANALOGY"
    BY_VERIFIED_MODEL = "BY_VERIFIED_MODEL"

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


@dataclass
class ManufacturerModel:
    normal_form: str
    status: ManufacturerStatus
    # original_manufacturer: 'ManufacturerModel' = None


@dataclass
class ModelModel:
    normal_form: str
    manufacturer: 'ManufacturerModel' = None
    essence: str = None
    series: str = None
    # original_model: 'ModelModel' = None
