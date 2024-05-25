import logging

import telebot.apihelper

import database as db
import schedule
import threading
import time

from telebot import TeleBot, types
from functions import get_telegram_token, is_time, is_appropriate_message
from config import *


logging.basicConfig(filename=LOGS, level=logging.INFO,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

bot = TeleBot(get_telegram_token())
db.create_table()


@bot.message_handler(commands=["start", "help"])
def wellcome(message: types.Message):
    bot.send_message(message.chat.id, bot_answers[message.text], reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=["add_schedule"])
def add_schedule(message: types.Message):
    mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    mk.add("Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота")

    bot.send_message(message.chat.id, "Выбери день недели", reply_markup=mk)
    bot.register_next_step_handler(message, get_day_week, "add")


def get_schedule(message: types.Message, day_week, mode):
    chat_id = message.chat.id

    status, content = is_appropriate_message(message, [message.text])
    if not status:
        bot.send_message(message.chat.id, content)
        get_schedule(message, day_week, mode)
        return
    if message.text.lower() == "отмена":
        bot.send_message(chat_id, "Отменено")
        return

    new_message = ""
    id_lesson = 0
    try:
        for lesson in message.text.split("/"):
            id_lesson += 1
            new_message += F"{id_lesson}. {lesson}\n"
    except ValueError:
        bot.send_message(chat_id, "Введите своё расписание по предложенному формату")
        bot.register_next_step_handler(message, get_schedule, day_week)
        return
    mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    mk.add("ДА", "ПЕРЕДЕЛАТЬ")

    bot.send_message(chat_id, new_message + "\n\nВсё верно?", reply_markup=mk)
    bot.register_next_step_handler(message, checking_for_schedule, message.text, day_week, mode)


def checking_for_schedule(message, text, day_week, mode):
    status, content = is_appropriate_message(message, ["ДА", "ПЕРЕДЕЛАТЬ"])
    if not status:
        bot.send_message(message.chat.id, content, reply_markup=types.ReplyKeyboardRemove())
        return

    if message.text == "ПЕРЕДЕЛАТЬ":
        add_schedule(message)
        return
    if message.text == "ДА":
        id_lesson = 0
        if mode == "replace":
            db.delete_schedule(message.chat.id, day_week)
        for lesson in text.split("/"):
            id_lesson += 1
            db.insert_schedule_to_db(message.chat.id, day_week, id_lesson, lesson)

        bot.send_message(message.chat.id, "Добавлено✅", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=["sent_schedule"])
def sent_schedule(message: types.Message):
    mk = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    mk.add("Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота")

    bot.send_message(message.chat.id, "Выбери день недели", reply_markup=mk)
    bot.register_next_step_handler(message, get_day_week, "sent")


def get_sent_schedule(chat_id, day_week):
    try:
        text = ""
        for i in db.get_schedule(chat_id, day_week):
            text += f"{i[0]}. {i[1]}\n"
        bot.send_message(chat_id, text, reply_markup=types.ReplyKeyboardRemove())

    except Exception as e:
        bot.send_message(chat_id, "На этот день расписания нет", reply_markup=types.ReplyKeyboardRemove())
        logging.error(e)


def get_day_week(message: types.Message, mode):
    chat_id = message.chat.id
    try:
        status, content = is_appropriate_message(message,
                                                 ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"])
        if not status:
            bot.send_message(message.chat.id, content)
            return

        day_week = message.text

        if mode == "add":
            bot.send_message(chat_id, f"Напиши своё расписание на {day_week} в формате:\n{FORMAT_SCHEDULE}", reply_markup=types.ReplyKeyboardRemove())

            if db.get_schedule(chat_id, day_week):
                get_sent_schedule(message.chat.id, day_week)
                bot.send_message(chat_id, "Сверху ваше расписание на этот день. Если не хотите его менять напишите Отмена")
                bot.register_next_step_handler(message, get_schedule, day_week, "replace")
                return

            bot.register_next_step_handler(message, get_schedule, day_week, "add")
        if mode == "sent":
            get_sent_schedule(message.chat.id, day_week)
    except Exception as e:
        logging.error(e)


@bot.message_handler(commands=["setting_notification"])
def setting_notification(message: types.Message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(*[types.KeyboardButton(text) for text in ['Установить время', 'Настроить дни недели']])
    bot.send_message(chat_id, '❗Сначала настройте дни потом время. Выберите действие:', reply_markup=markup)
    try:
        notification_ = db.select_notification()
        if notification_:
            bot.send_message(chat_id, f"Уведомления будут приходить вам по: {[i[2] for i in notification_]}. В {notification_[0][1]}")
        bot.register_next_step_handler(message, options)
    except Exception as e:
        logging.error(e)


def options(message: types.Message):
    chat_id = message.chat.id
    option = message.text
    try:
        status, content = is_appropriate_message(message, ['Установить время', 'Настроить дни недели', "Отмена"])
        if not status:
            bot.send_message(message.chat.id, content, reply_markup=types.ReplyKeyboardRemove())
            return
        elif option.lower() == "отмена":
            bot.send_message(chat_id, "Отменено", reply_markup=types.ReplyKeyboardRemove())
            return

        elif option == 'Установить время':
            message = bot.send_message(chat_id, 'Введите время в формате ЧЧ:ММ')
            bot.register_next_step_handler(message, set_time)
        elif option == 'Настроить дни недели':
            markup = types.InlineKeyboardMarkup()
            markup.add(*[types.InlineKeyboardButton(day, callback_data=day)
                         for day in
                         ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']])
            bot.send_message(chat_id, 'Выберите дни недели:', reply_markup=markup)
    except Exception as e:
        logging.error(e)


def set_time(message: types.Message):
    chat_id = message.chat.id
    time = message.text
    try:
        status, content = is_appropriate_message(message, [message.text])
        if not status:
            bot.send_message(message.chat.id, content)
            setting_notification(message)
            return
        if is_time(time):
            db.update_db(chat_id, columns=("time_notification",), values=(time,), replace=True)
            notifications(message)
            bot.send_message(chat_id, f'Время установлено на {time}.', reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.send_message(chat_id, "Нужно ввести время в формате ЧЧ:ММ", reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        logging.error(e)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    day = call.data
    try:
        # Получение списка дней для данного чата
        current_days = db.get_data_from_db(chat_id, "day_notification", notification_mode=True)
        if day not in current_days:
            db.add_day(chat_id, day)
            bot.answer_callback_query(call.id, f'День {day} добавлен.')
        else:
            db.remove_day(chat_id, day)
            bot.answer_callback_query(call.id, f'День {day} удален.')
        notifications(call.message)
    except Exception as e:
        logging.error(e)


def notification(chat_id):
    try:
        text, status = sent_homework(chat_id)
        bot.send_message(chat_id, text, reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        logging.error(e)
        bot.send_message(chat_id, "У вас нет домашнего задания", reply_markup=types.ReplyKeyboardRemove())


def notifications(message: types.Message):
    try:
        schedule.clear()
        for chat_id, time_notification, day_notification in db.select_notification():
            if day_notification == "Понедельник":
                schedule.every().monday.at(time_notification).do(notification, chat_id)
            elif day_notification == "Вторник":
                schedule.every().tuesday.at(time_notification).do(notification, chat_id)
            elif day_notification == "Среда":
                schedule.every().wednesday.at(time_notification).do(notification, chat_id)
            elif day_notification == "Четверг":
                schedule.every().thursday.at(time_notification).do(notification, chat_id)
            elif day_notification == "Пятница":
                schedule.every().friday.at(time_notification).do(notification, chat_id)
            elif day_notification == "Суббота":
                schedule.every().saturday.at(time_notification).do(notification, chat_id)
            elif day_notification == "Воскресенье":
                schedule.every().sunday.at(time_notification).do(notification, chat_id)
            else:
                bot.send_message(message.chat.id, "Вы не выбрали время или дни недели для отправки уведомления", reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        logging.error(e)


# Добро пожаловать в говнокод
@bot.message_handler(commands=["sent_homework"])
def send_homework_now(message):
    chat_id = message.chat.id
    text, status = sent_homework(chat_id)
    try:
        if status:
            bot.send_message(chat_id, text)
            bot.send_message(chat_id, "Чтобы убрать дз из списка введите его номер", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, delete_homework)
            return
        else:
            bot.send_message(chat_id, "У вас нет домашнего задания")
    except telebot.apihelper.ApiTelegramException:
        bot.send_message(chat_id, "У вас нет домашнего задания", reply_markup=types.ReplyKeyboardRemove())


def sent_homework(chat_id):
    db.insert_user_to_db(chat_id)

    if not db.get_data_from_db(chat_id, columns="homework"):
        return "У вас нет домашнего задания", False

    homework_list = [f"{index + 1}. {item}\n" for index, item in
                     enumerate(db.get_data_from_db(chat_id, columns="homework")[0][0].split(',')) if item != ""]
    text = "".join(homework_list)
    return text, True


def delete_homework(message):
    chat_id = message.chat.id
    try:
        nums = range(1, len([i for i in db.get_data_from_db(chat_id, columns="homework")[0][0].split(',')[:-1] if i != ""]))
        if int(message.text) not in nums:
            bot.send_message(chat_id, "Нет такого номера дз", reply_markup=types.ReplyKeyboardRemove())
            return
    except:
        bot.send_message(chat_id, "Нет такого номера дз", reply_markup=types.ReplyKeyboardRemove())
        return
    curr_hw = [i for i in db.get_data_from_db(chat_id, columns="homework")[0][0].split(',')[:-1] if i != ""]
    curr_hw.pop(int(message.text) - 1)
    db.update_db(chat_id, columns=("homework",), values=(",".join(curr_hw) + ",",))
    bot.send_message(chat_id, f"Дз {message.text} удалено", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=["get_homework"])
def get_homework(message):
    bot.send_message(message.chat.id, "Отправьте дз через запятую", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, add_homework_to_db)


def add_homework_to_db(message):
    db.insert_user_to_db(message.chat.id)
    db.update_db(message.chat.id, columns=("homework",), values=(message.text + ',',), replace=False)
    bot.send_message(message.chat.id, "Дз получено", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=["GPT_help"])
def GPT_help(message):
  bot.sent_message(message.chat.id, "Введите своё задание, я попытаюсь его решить")
  bot.register_next_step_handler(message, ask_gpt)





def run_polling():
    try:
        bot.polling()
    except Exception as e:
        logging.critical(e)


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)  # Делаем небольшую паузу перед следующим циклом


# Запускаем два потока: один для polling, другой для scheduler
polling_thread = threading.Thread(target=run_polling)
scheduler_thread = threading.Thread(target=run_scheduler)

# Запускаем потоки
polling_thread.start()
scheduler_thread.start()

# Ожидаем завершения потоков
polling_thread.join()
scheduler_thread.join()
