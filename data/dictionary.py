import pymorphy2

from algorithms.merge_soft import MergedToken
from data.essence import essences
from tokens import Token, CyrillicToken, Context, Sep

dictionary = {
    'зиговочный',
    'клеенанесения',
    'клеенанесение',
    'трехфазный',
    'металлорукав',
    'погружный',
    'электронасосный',
    'кромкооблицовочный',
    'тефлоновая',
    'токопроводный',
    'рутилово',
    'целлюлозный',
    'пропановый',
    'полугерметичный',
    'тэновый',
    'рефрежираторный',


}.union(essences)

morph = pymorphy2.MorphAnalyzer()


def is_token_in_cyrillic_dictionary(context: Context, token: Token):
    if not (isinstance(context.next, Sep) and (context.value_index <= 0 or isinstance(context.prev, Sep))):
        return False
    if isinstance(token, MergedToken) and '-' in token.value:
        splt = token.value.split('-')
        return is_word_in_cyrillic_dictionary(splt[0]) and is_word_in_cyrillic_dictionary(splt[1])
    elif isinstance(token, CyrillicToken):
        return is_word_in_cyrillic_dictionary(token.value)
    return False


def is_word_in_cyrillic_dictionary(word: str):
    w = morph.parse(word)[0]
    if w.normal_form.lower() in dictionary or word.lower() in dictionary:
        return True
    if not w.is_known:
        return False
    if any(s.isupper() for s in word):
        if 'Abbr' in w[1].grammemes:
            return False
        if 'INTJ' in w[1].grammemes:
            return False
    return True
