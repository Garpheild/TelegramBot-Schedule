import re
from telebot import types

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
        return False, "Введите тестовое сообщение"
    if message.text not in message_list:
        return False, "Введите ответ из предложенных"
    return True, ""
