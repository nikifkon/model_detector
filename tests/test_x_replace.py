import pytest

from tokens import TokenSeq
from algorithms.x_replace import XReplace


@pytest.mark.parametrize('input, output', [
    ('Коллекторы KIT BASE ZNT VER Galvanized Steel 380x300', 'Коллекторы KIT BASE ZNT VER Galvanized Steel 380×300'),
    ('Насос Grundfos ALPHA2 L 25-60 180 1x230B', 'Насос Grundfos ALPHA2 L 25-60 180 1×230B'),
    ('Распашные двери серии «Оптима» РДО 800х1900, 80 мм', 'Распашные двери серии «Оптима» РДО 800×1900, 80 мм'),
    ('Шкаф шокового охлаждения вместимостью 10*GN1/1 или 40*60 см (36 кг) Angelo Po XA101L', 'Шкаф шокового охлаждения вместимостью 10*GN1/1 или 40×60 см (36 кг) Angelo Po XA101L'),
    ('Св-05Х19Н9Ф3С2 3x3mm', 'Св-05Х19Н9Ф3С2 3×3mm'),
    ('Св3x3mm', 'Св3×3mm'),
])
def test_x_replace(input: str, output: str):
    res = XReplace().parse(input)
    assert str(res.seq) == output


@pytest.mark.parametrize('input, output', [
    ('Коллекторы KIT BASE ZNT VER Galvanized Steel 380x300', 'Коллекторы KIT BASE ZNT VER Galvanized Steel 380×300')
])
def test_x_replace__token_iterface(input: str, output: str):
    seq = TokenSeq.from_string(input)
    res = XReplace().parse_by_tokens(seq)
    assert str(res.seq) == output
