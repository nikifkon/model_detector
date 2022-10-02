PREFIXES_RU = ["да", "д", "с", "мк", "м", "н", "п", "г", "к", "М", "Г", "Т", "П"]
PREFIXES_EN = ["da", "d", "c", "m", "µ", "n", "p", "h", "k", "M", "G", "T", "P"]
PREFIXES = PREFIXES_RU + PREFIXES_EN
SUFFIXES = {
    "^3": '^3',
    "^2": '^2',
    "3": '^3',
    "2": '^2',
    "³": '^3',
    "²": '^2'
}


class NumberTypes:
    plain = "plain"
    with_dot = "with_dot"
    with_comma = "with_comma"
    dashed = "dashed"
    xed = "xed"

    @classmethod
    def get_types(cls, string):
        res = set([cls.plain])
        if '.' in string:
            res.add(cls.with_dot)
        if ',' in string:
            res.add(cls.with_comma)
        if '-' in string:
            res.add(cls.dashed)
        if '×' in string:
            res.add(cls.xed)
        return res


ALL_TYPES = set([
    NumberTypes.plain,
    NumberTypes.with_dot,
    NumberTypes.with_comma,
    NumberTypes.dashed,
    NumberTypes.xed,
])

STANDART_NUMBER = set([
    NumberTypes.plain,
    NumberTypes.with_dot,
    NumberTypes.with_comma
])

NATURAL_NUMBER = set([NumberTypes.plain])


UNIT_MAP = {
    # литра
    # литров
    # литр
    "л": {
        "types": STANDART_NUMBER,
        "name": "Объем",
        "allow_suffix": False,
        "allow_prefix": True
    },
    "м": (metr := {
        "types": ALL_TYPES,
        "name": "Размер",
        "plural_name": "Габариты",
        "allow_suffix": True,
        "allow_prefix": True
    }),
    "m": metr,
    "фут": metr,
    "в": (volt := {
        "types": ALL_TYPES,
        "name": "Напряжение",
        "allow_suffix": False,
        "allow_prefix": True
    }),
    "v": volt,
    "вт": (vatt := {
        "types": ALL_TYPES,
        "name": "Мощность",
        "allow_suffix": False,
        "allow_prefix": True
    }),
    "w": vatt,
    "с": (sec := {
        "types": STANDART_NUMBER,
        "name": "Время",
        "banned": True,
        "allow_suffix": True
    }),
    "s": sec,
    "мин": (min := {
        "types": STANDART_NUMBER,
        "name": "Время",
        "allow_suffix": False,
        "allow_prefix": False
    }),
    "min": min,
    "ч": min,
    "час": min,
    "h": min,
    "а": (amper := {
        "types": STANDART_NUMBER,
        "name": "Сила тока",
        "allow_suffix": False,
        "allow_prefix": True
    }),
    "a": amper,
    "шт": (count := {
        "types": NATURAL_NUMBER,
        "name": "Количество",
        "allow_prefix": False
    }),
    "г": (gramm := {
        "types": STANDART_NUMBER,
        "name": "Масса",
        "allow_suffix": False,
        "allow_prefix": True
    }),
    "g": gramm,
    "т": gramm,
    "гр": gramm,
    "об": {
        "types": NATURAL_NUMBER,
        "name": "Количество оборотов",
        "allow_suffix": False,
        "allow_prefix": False
    },
    "гц": (gerz := {
        "types": STANDART_NUMBER,
        "name": "Частота",
        "allow_suffix": False,
        "allow_prefix": True
    }),
    "hz": gerz,
    "атм": (pressure := {
        "types": STANDART_NUMBER,
        "name": "Давление",
        "allow_suffix": False,
        "allow_prefix": False
    }),
    "па": {
        "types": STANDART_NUMBER,
        "name": "Давление",
        "allow_suffix": False,
        "allow_prefix": True
    },
    "об/мин": (ob := {
        "types": STANDART_NUMBER,
        "name": "Частота вращения"
    }),
    "об/м": ob,
    "л/мин": (productivity := {
        "types": STANDART_NUMBER,
        "name": "Производительность"
    }),
    "г/л": productivity,
    "g/м": productivity,
    "г/м": productivity,
    "гр/м": productivity,
    "л/м": productivity,
    "л/ч": productivity,
    "л/час": productivity,
    "м/мин": productivity,
    "m/min": productivity,
    "m/ч": productivity,
    "м/ч": productivity,
    "м/час": productivity,
    "т/мин": productivity,
    "т/ч": productivity,
    "т/час": productivity,
    "г/мин": productivity,
    "г/ч": productivity,
    "г/час": productivity,
    "г/м2": productivity,
    "шт/ч": productivity,
    "шт/час": productivity,
    "вт/ч": productivity,
    "вт/час": productivity,
    "вт/шт": productivity,
}
