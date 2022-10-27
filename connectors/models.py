from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ManufacturerStatus(Enum):
    VERIFIED = "VERIFIED"
    FROM_PULSCEN = "FROM_PULSCEN"
    FROM_SATOM = "FROM_SATOM"
    MANUAL = "MANUAL"
    BY_STATISTIC = "BY_STATISTIC"
    BANNED = "BANNED"
    # MULTY = "MULTY"


class ManufacturerMethod(Enum):
    FROM_DATA = "FROM_DATA"
    BY_NAME_CLEAR = "BY_NAME_CLEAR"
    BY_SERIES = "BY_SERIES"
    BY_NAME_DRY = "BY_NAME_DRY"
    BY_ANALOGY = "BY_ANALOGY"
    BY_VERIFIED_MODEL = "BY_VERIFIED_MODEL"
    MULTY = "MULTY"
    MISSED = "MISSED"


class SeriesStatus(Enum):
    VERIFIED = "VERIFIED"
    BY_STATISTIC = "BY_STATISTIC"
    BANNED = "BANNED"


@dataclass(eq=True, frozen=True)
class ManufacturerModel:
    normal_form: str
    status: ManufacturerStatus


@dataclass(eq=True, frozen=True)
class ModelModel:
    normal_form: str
    manufacturer: Optional['ManufacturerModel'] = None
    essence: Optional[str] = None
    series: Optional['SeriesModel'] = None

    @property
    def normal_form_with_series(self):
        if self.series:
            return self.series.normal_form + ' ' + self.normal_form
        return self.normal_form


@dataclass(eq=True, frozen=True)
class SeriesModel:
    normal_form: str
    status: SeriesStatus
    manufacturer: Optional['ManufacturerModel'] = None


MODEL_PREFIX = 'model:'
MANUFACTURER_PREFIX = 'manufacturer:'
SERIES_PREFIX = 'series:'
