import logging
import database as db

from telebot import TeleBot, types
from get_creds import get_telegram_token
from config import *


logging.basicConfig(filename=LOGS, level=logging.INFO,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

bot = TeleBot(get_telegram_token())


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


bot.polling()
