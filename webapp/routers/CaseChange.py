import pymorphy2

def StartCase(text_list):
    new_list = []
    morph = pymorphy2.MorphAnalyzer()

    for el in text_list:
        # Если слово не русское — просто нормализуем
        if not any('а' <= ch <= 'я' or 'А' <= ch <= 'Я' for ch in el):
            new_list.append(el.capitalize())
            continue

        p = morph.parse(el)[0]
        gent = p.inflect({'gent'})

        if gent is None:          # <-- ВАЖНАЯ ПРОВЕРКА
            word = el.capitalize()
        else:
            word = gent.word.capitalize()

        new_list.append(word)

    return new_list
