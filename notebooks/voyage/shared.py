def area_normalize_ru(s):
    stopword = "район"
    
    abbreviations = {"административный округ": "АО"}
    s = s.replace(stopword, "").strip()
    for x in abbreviations:
        s = s.replace(x, abbreviations[x]).strip()
    return s


def street_normalize_ru(s):
    abbreviations = {'Улица': 'Ул.', 
                     'Проспект': 'Пр-т', 
                     'Набережная': 'Наб.', 
                     'Проезд': 'Пр-д', 
                     'Бульвар': 'Бул.',
                     'Площадь': 'Пл.',
                     'Крепость': 'Кр-ть'}
    for x in abbreviations:
        s = s.replace(x, abbreviations[x]).strip()
    return s


def title(s): 
    return s.title()


def trim(s, max_len=20):
    if len(s) <= max_len:
        return s
    else:
        s = s[:max_len].strip("_")
        return s + "..."
