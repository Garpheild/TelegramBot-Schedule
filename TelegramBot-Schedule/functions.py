import os
import logging
import re
from telebot import types
from config import *

logging.basicConfig(filename=LOGS, level=logging.INFO,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")


def get_telegram_token():
    if not os.path.exists(TG_TOKEN):
        logging.critical(f"Файл {TG_TOKEN} не найден.")
        raise FileNotFoundError(f"Файл '{TG_TOKEN} не найден.")
    try:
        with open(os.path.join(TG_TOKEN), "r") as file:
            telegram_token = file.read().strip()
            return telegram_token
    except IOError as e:
        logging.critical(f"Ошибка при чтении файла {TG_TOKEN}: {e}")
        print(f"Ошибка при чтении файла {TG_TOKEN}: {e}")


def is_time(text):
    # Регулярное выражение для проверки формата времени
    time_pattern = r'^([0-1]?[0-9]|2[0-3]):([0-5][0-9])(?::([0-5][0-9]))?$'

    # Проверяем, соответствует ли текст шаблону времени
    if re.match(time_pattern, text):
        return True
    else:
        return False


def is_appropriate_message(message: types.Message, message_list):
    if message.content_type != "text":
        return False, "Введите текстовое сообщение"
    if message.text not in message_list:
        return False, "Введите ответ из предложенных в кнопках"
    return True, ""


