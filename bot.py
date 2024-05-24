import logging
import database as db

from telebot import TeleBot, types
from get_creds import get_telegram_token
from config import *


logging.basicConfig(filename=LOGS, level=logging.INFO,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

bot = TeleBot(get_telegram_token())

def add_buttons(buttons):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons)
    return keyboard
  

@bot.message_handler(commands=["start", "help"])
def wellcome(message: types.Message):
    bot.send_message(message.chat.id, bot_answers[message.text])


@bot.message_handler(commands=[""])
def add_schedule(message: types.Message):
    mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    mk.add("Понедельник, Вторник, Среда, Четверг, Пятница, Суббота")

    bot.send_message(message.chat.id, "Выбери день недели", reply_markup=mk)
    bot.register_next_step_handler(message, get_day_week, mode="add")


def get_day_week(message : types.Message, mode):

    #провека на текст

    day_week = message.text

    if mode == "add":
        bot.register_next_step_handler(message, get_schedule, day_week = day_week)
    if mode == "sent":
        bot.register_next_step_handler(message, get_sent_schedule, day_week=day_week)



def get_schedule(message: types.Message, day_week):
    chat_id = message.chat.id

    lesson, name, time = #функция деления рассписания на id урока, название предмета, время по day week

    #сохранение каждого пункта в базу данных
    db.insert_user_to_db(chat_id, lesson, name, time)



@bot.message_handler(commands=["sent_schedule"])
def sent_schedule(message: types.Message):
    mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    mk.add("Понедельник, Вторник, Среда, Четверг, Пятница, Суббота")

    bot.send_message(message.chat.id, "Выбери день недели", reply_markup=mk)
    bot.register_next_step_handler(message, get_day_week, mode="add")


def get_sent_schedule(message: types.Message):
    #из списков в списке формируется расписание
    pass


@bot.message_handler(commands=["setting_schedule"])
def setting_schedule(message: types.Message):
    #пишет Радан
    pass


@bot.message_handler(commands=["get_homework"])
def get_homework(message: types.Message):
    bot.send_message(message.chat.id, "Что вам задали и по какому предмету?")
    bot.register_next_step_handler(message, homework_hendler)


def homework_hendler(message):
    #добавление в базу данных
    bot.send_message(message.chat.id, "Добавлено✅")


@bot.message_handler(commands=["sent_homework"])
def sent_homework(message: types.Message):
    #отправляется весь список домашнего задания с кнопками по которым


#Добро пожаловать в говнокод
@bot.message_handler(func=lambda message: message.text == "Получить дз")
def send_homework(message):
    chat_id = message.chat.id
    db.insert_user_to_db(chat_id)

    if not db.get_data_from_db(chat_id, columns="homework")[0][0]:
        bot.send_message(chat_id, "У вас нет домашнего задания")
        return
    
    homework_list = [f"{index + 1}. {item}\n" for index, item in enumerate(db.get_data_from_db(chat_id, columns="homework")[0][0].split(',')) if item != ""]

    bot.send_message(chat_id, "".join(homework_list))
    bot.send_message(chat_id, "Чтобы убрать дз из списка введите его номер")
    bot.register_next_step_handler(message, delete_homework)


def delete_homework(message):
    chat_id = message.chat.id
    nums = range(1, len(db.get_data_from_db(chat_id, columns="homework")[0][0].split(',')) - 1)
    print(nums)
    if int(message.text) not in nums:
        bot.send_message(chat_id, "Нет такого номера дз")
        return
    curr_hw = db.get_data_from_db(chat_id, columns="homework")[0][0].split(',')[:-1]
    print(curr_hw)
    curr_hw.pop(int(message.text) - 1)
    print(curr_hw)
    db.update_db(chat_id, columns=("homework",), values=(",".join(curr_hw),))
    bot.send_message(chat_id, f"Дз {message.text} удалено")

@bot.message_handler(func=lambda message: message.text == "Отправить дз")
def get_homework(message):
    bot.send_message(message.chat.id, "Отправьте дз через запятую")
    bot.register_next_step_handler(message, add_homework_to_db)


def add_homework_to_db(message):
    db.insert_user_to_db(message.chat.id)
    db.update_db(message.chat.id, columns=("homework",), values=(message.text + ',',), replace=False)
    bot.send_message(message.chat.id, "Дз получено")


bot.polling()
