import pymorphy2

from tokens import Context, Token

morph = pymorphy2.MorphAnalyzer()

essences = {
    'эжектор',
    'камнерез',
    'пилорама',

    'трубогиб',
    'трубогибы',

    'ротор',
    'листогиб',
    'многопил',
    'профилегиб',
    'фальцегиб',
    'мотопомпа',

    'позиционер',
    'виброгаситель',
    'маслоуказатель',
    'разлучка'
}


def can_be_essence(context: Context, token: Token):
    not_abbr = not (context.next and '.' in context.next.value)
    word = morph.parse(token.value)[0]
    if token.value.lower() in essences:
        return True
    elif is_noun(word) and not_abbr and is_normal_form(word):
        return True
    return False


def is_normal_form(w):
    norm = w.normal_form
    s = {norm}
    plur = w.inflect({'plur', 'nomn'})
    if plur:
        s.add(plur.word)
    return w.word in s


def is_noun(w):
    return 'NOUN' in w.tag
