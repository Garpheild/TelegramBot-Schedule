import json
from config import JSON

def save_dict_to_json(dictionary):
    """Сохраняет словарь в файл JSON."""
    with open(JSON, 'w', encoding='utf-8') as file:
        json.dump(dictionary, file, ensure_ascii=False, indent=4)

def load_dict_from_json():
    """Достает словарь из файла JSON."""
    with open(JSON, 'r', encoding='utf-8') as file:
        return json.load(file)
