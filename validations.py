import re





def validate_empire_id(empire_id):
    try:
        empire_id_number = int(empire_id)
        return 3011111 <= empire_id_number <= 9999999
    except ValueError:
        return False






def validate_positive_number(value):
    try:
        value_number = int(value)
        return value_number > 0
    except ValueError:
        return False



FORBIDDEN_WORDS = {
    "тест"
}

def is_valid_empire_name(name: str) -> bool:
    name = name.strip()

    if not (3 <= len(name) <= 26):
        return False

    if not re.fullmatch(r"[а-яА-Яa-zA-Z0-9 _]+", name):
        return False

    if not re.match(r"[а-яА-Яa-zA-Z]", name[0]):
        return False

    if not re.search(r"[а-яА-Яa-zA-Z]", name):
        return False

    if any(forbidden in name.lower() for forbidden in FORBIDDEN_WORDS):
        return False

    return True
