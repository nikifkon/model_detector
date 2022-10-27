from itertools import product

PREFIXES_RU = ["да", "д", "с", "мк", "м", "н", "п", "г", "к", "М", "Г", "Т", "П"]
PREFIXES_EN = ["da", "d", "с", "m", "µ", "n", "p", "h", "k", "M", "G", "T", "P"]
PREFIXES_SPECIAL = ['куб.', 'кв.']
PREFIXES = PREFIXES_SPECIAL + PREFIXES_RU + PREFIXES_EN
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


ALL_TYPES = {
    NumberTypes.plain,
    NumberTypes.with_dot,
    NumberTypes.with_comma,
    NumberTypes.dashed,
    NumberTypes.xed,
}

STANDART_NUMBER = {
    NumberTypes.plain,
    NumberTypes.with_dot,
    NumberTypes.with_comma
}

NATURAL_NUMBER = {NumberTypes.plain}

UNIT_MAP = {
    "л": (litr := {
        "types": STANDART_NUMBER,
        "name": "Объем",
        "allow_suffix": False,
        "allow_prefix": True,
        "standard": "л",
    }),
    "литр": litr,
    "литра": litr,
    "литров": litr,

    "бар": (barrel := {
        "types": STANDART_NUMBER,
        "name": "Объем",
        "allow_suffix": False,
        "allow_prefix": True,
        "standard": "бар"
    }),
    "баррель": barrel,
    "м": (metr := {
        "types": ALL_TYPES,
        "name": "Размер",
        "plural_name": "Габариты",
        "allow_suffix": True,
        "allow_prefix": True,
        "standard": "м"
    }),
    "m": metr,
    "метр": metr,
    "метров": metr,
    "метра": metr,
    "фут": (ft := {
        "types": ALL_TYPES,
        "name": "Размер",
        "plural_name": "Габариты",
        "allow_suffix": False,
        "allow_prefix": False,
        "standard": "фут"
    }),
    "футов": ft,
    "фута": ft,
    "в": (volt := {
        "types": ALL_TYPES,
        "name": "Напряжение",
        "allow_suffix": False,
        "allow_prefix": False,
        "standard": "В"
    }),
    "v": volt,
    "вольт": volt,
    "вт": (vatt := {
        "types": ALL_TYPES,
        "name": "Мощность",
        "allow_suffix": False,
        "allow_prefix": True,
        "standard": "ВТ"
    }),
    "w": vatt,
    "ватт": vatt,
    "с": (sec_banned := {
        "types": STANDART_NUMBER,
        "name": "Время",
        "banned": True,
        "allow_suffix": True,
        "allow_prefix": False,
        "standard": "с"
    }),
    "секунд": (sec := {
        "types": STANDART_NUMBER,
        "name": "Время",
        "allow_suffix": False,
        "allow_prefix": False,
        "standard": "с"
    }),
    "секунда": sec_banned,
    "мин": (min := {
        "types": STANDART_NUMBER,
        "name": "Время",
        "allow_suffix": False,
        "allow_prefix": False,
        "standard": "мин"
    }),
    "min": min,
    "минут": min,
    "минута": min,
    "минуты": min,
    "ч": (hour := {
        "types": STANDART_NUMBER,
        "name": "Время",
        "allow_suffix": False,
        "allow_prefix": False,
        "standard": "ч"
    }),
    "час": hour,
    "часов": hour,
    "часа": hour,
    "h": hour,
    "а": (amper := {
        "types": STANDART_NUMBER,
        "name": "Сила тока",
        "allow_suffix": False,
        "allow_prefix": True,
        "standard": "А"
    }),
    "a": amper,
    "ампер": amper,
    "амперов": amper,
    "ампера": amper,
    "шт": (count := {
        "types": NATURAL_NUMBER,
        "name": "Количество",
        "allow_prefix": False,
        "allow_suffix": False,
        "standard": "шт"
    }),
    "штук": count,
    "г": (gramm := {
        "types": STANDART_NUMBER,
        "name": "Масса",
        "allow_suffix": False,
        "allow_prefix": True,
        "standard": "г"
    }),
    "g": gramm,
    "гр": gramm,
    "тонн": (tonne := {
        "types": STANDART_NUMBER,
        "name": "Масса",
        "allow_suffix": False,
        "allow_prefix": True,
        "standard": "т"
    }),
    "т": tonne,
    "тонна": tonne,
    "тонны": tonne,
    "об": {
        "types": NATURAL_NUMBER,
        "name": "Количество оборотов",
        "allow_suffix": False,
        "allow_prefix": False,
        "standard": "об"
    },
    "гц": (gerz := {
        "types": STANDART_NUMBER,
        "name": "Частота",
        "allow_suffix": False,
        "allow_prefix": True,
        "standard": "гц"
    }),
    "hz": gerz,
    "атм": (pressure := {
        "types": STANDART_NUMBER,
        "name": "Давление",
        "allow_suffix": False,
        "allow_prefix": False,
        "standard": "атм"
    }),
    "па": {
        "types": STANDART_NUMBER,
        "name": "Давление",
        "allow_suffix": False,
        "allow_prefix": True,
        "standard": "па"
    },
    "об/мин": (ob := {
        "types": STANDART_NUMBER,
        "name": "Частота вращения",
        "allow_suffix": False,
        "allow_prefix": False,
        "standard": "об/мин"
    }),
    "об/м": ob,
}

left_productive = ['л', 'м', 'm', 'т', 'г', 'гр', 'g', 'шт', 'вт', 'об']
right_productive = ['м', 'мин', 'min', 'ч', 'час', 'h', 'шт', 'с', 'сек', 'м2']
sep = ['/', '.']

for left, s, right in product(left_productive, sep, right_productive):
    if left + s + right in UNIT_MAP:
        continue
    UNIT_MAP[left + s + right] = {
        "types": STANDART_NUMBER,
        "name": "Производительность",
        "allow_suffix": False,
        "allow_prefix": False,
        "standard": left + "/" + right
    }

PROPERTY_NAMES = {
    'd': (diam := {
        "units": {'м', 'фут'},
        "standard": "Диаметр"
    }),
    'diam': diam,
    'Ø': diam,
    'диам': diam,
    'диаметр': diam,
    'глубина': (depth := {
        "units": {'м', 'фут'},
        "standard": "Глубина",
    }),
    'мощность': (power := {
        "units": {'вт'},
        "standard": "Мощность",
    }),
    "длина": (length := {
        "units": {'м', 'фут'},
        "standard": "Длина",
    }),
    'l': length,
    'высота': (height := {
        "units": {'м', 'фут'},
        "standard": "Высота",
    }),
    'h': height,
}
