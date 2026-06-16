import json
from pathlib import Path


class I18N:
    def __init__(self, lang="ru"):
        self.lang = lang
        self.translations = self.load_locale(lang)

    def load_locale(self, lang):
        path = Path(__file__).resolve().parent / "locales" / f"{lang}.json"
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def t(self, key, **kwargs):
        keys = key.split(".")
        value = self.translations
        for k in keys:
            value = value[k]
        return value.format(**kwargs) if kwargs else value


















