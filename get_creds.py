import os
import logging

from config import *

logging.basicConfig(filename=LOGS, level=logging.INFO,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")


def get_telegram_token():
    if not os.path.exists(TG_TOKEN):
        logging.critical("Файл 'CP.txt' не найден.")
        raise FileNotFoundError("Файл 'CP.txt' не найден.")
    try:
        with open(os.path.join(TG_TOKEN), "r") as file:
            telegram_token = file.read().strip()
            return telegram_token
    except IOError as e:
        logging.critical(f"Ошибка при чтении файла 'CP.txt': {e}")
        print(f"Ошибка при чтении файла 'CP.txt': {e}")
