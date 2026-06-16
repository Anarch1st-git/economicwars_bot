import random
import re
from models import (
    UserData,
    Empire
)


def generate_unique_chat_id():
    """Генерирует уникальный chat_id, проверяя его в БД"""
    while True:
        chat_id = int(''.join(random.choices('0123456789', k=10)))
        if not UserData.select().where(UserData.chat_id == chat_id).exists():
            return chat_id



LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯабвгдеёжзийклмнопрстуфхцчшщьыъэюя"
ALLOWED_CHARS = LETTERS + "0123456789 _"


BANNED_WORDS = {"оскорбление", "мат", "экстремизм"}

def generate_empire_name():
    """Генерирует уникальное имя империи, проверяя его в БД"""
    LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯабвгдеёжзийклмнопрстуфхцчшщьыъэюя"
    ALLOWED_CHARS = LETTERS + "0123456789 _"

    while True:
        length = random.randint(3, 26)
        name = ''.join(random.choices(ALLOWED_CHARS, k=length)).strip()

        if name[0] not in LETTERS:
            continue
        if not any(c in LETTERS for c in name):
            continue

        if not Empire.select().where(Empire.name == name).exists():
            return name
