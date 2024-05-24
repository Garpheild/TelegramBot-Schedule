import json.decoder
import logging
import database as db
import schedule
import threading
import time

from telebot import TeleBot, types
from get_creds import get_telegram_token
from config import *
from checks import is_time, is_appropriate_message
from json_funk import save_dict_to_json, load_dict_from_json

logging.basicConfig(filename=LOGS, level=logging.INFO,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

bot = TeleBot(get_telegram_token())
db.create_table()
try:
    users = load_dict_from_json()
except json.decoder.JSONDecodeError:
    users = {}


@bot.message_handler(commands=["start", "help"])
def wellcome(message: types.Message):
    chat_id = message.chat.id
    bot.send_message(chat_id, bot_answers[message.text])


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
        bot.register_next_step_handler(message, get_schedule, day_week)
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
        bot.send_message(message.chat.id, content)
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

        bot.send_message(message.chat.id, "Добавлено✅")


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
        bot.send_message(chat_id, text)

    except Exception as e:
        bot.send_message(chat_id, "На этот день расписания нет")
        logging.error(e)


@bot.message_handler(commands=["setting_notification"])
def setting_notification(message: types.Message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*[types.KeyboardButton(text) for text in ['Установить время', 'Настроить дни недели']])
    message = bot.send_message(chat_id, 'Выберите действие:', reply_markup=markup)
    try:
        if chat_id not in users:
            users[chat_id] = {'time': None, 'days': []}

        elif users[chat_id]['time'] and users[chat_id]['days']:
            bot.send_message(chat_id, f"Вы можете ввести Отмена и тогда уведомления будут приходить"
                                      f" вам по: {users[chat_id]['days']}. В {users[chat_id]['time']}")
            notifications(message)
        else:
            bot.send_message(message.chat.id, "Вы не выбрали время или дни недели отправки уведомления")

        bot.register_next_step_handler(message, options)
    except Exception as e:
        logging.error(e)


def options(message: types.Message):
    chat_id = message.chat.id
    option = message.text
    try:
        status, content = is_appropriate_message(message, ['Установить время', 'Настроить дни недели', "Отмена"])
        if not status:
            bot.send_message(message.chat.id, content)
            setting_notification(message)
            return
        elif option.lower() == "отмена":
            bot.send_message(chat_id, "Отменено")
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
            users[chat_id]['time'] = time
            setting_notification(message)
            bot.send_message(chat_id, f'Время установлено на {time}.')
        else:
            bot.send_message(chat_id, "Нужно ввести время в формате ЧЧ:ММ")
    except Exception as e:
        logging.error(e)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    day = call.data
    try:
        if day not in users[chat_id]['days']:
            users[chat_id]['days'].append(day)
            bot.answer_callback_query(call.id, f'День {day} добавлен.')
        else:
            users[chat_id]['days'].remove(day)
            bot.answer_callback_query(call.id, f'День {day} удален.')
        setting_notification(call.message)
    except Exception as e:
        logging.error(e)


def notification(chat_id):
    bot.send_message(chat_id, "НАПОМИНАНИЕ") #в оптимум будет отправка дз


def notifications(message: types.Message):
    try:
        schedule.clear()
        save_dict_to_json(users)
        for chat_id, user in users.items():
            if user['time'] and user['days']:
                for day in user['days']:
                    if day == "Понедельник":
                        schedule.every().monday.at(user['time']).do(notification, chat_id)
                    if day == "Вторник":
                        schedule.every().tuesday.at(user['time']).do(notification, chat_id)
                    if day == "Среда":
                        schedule.every().wednesday.at(user['time']).do(notification, chat_id)
                    if day == "Четверг":
                        schedule.every().thursday.at(user['time']).do(notification, chat_id)
                    if day == "Пятница":
                        schedule.every().friday.at(user['time']).do(notification, chat_id)
                    if day == "Суббота":
                        schedule.every().saturday.at(user['time']).do(notification, chat_id)
                    if day == "Воскресенье":
                        schedule.every().sunday.at(user['time']).do(notification, chat_id)
                    logging.info("Уведомления обновлены")
            else:
                bot.send_message(message.chat.id, "Вы не выбрали время или дни недели отправки уведомления")
    except Exception as e:
        logging.error(e)


@bot.message_handler(commands=["sent_homework"])#пока не работает
def send_homework(message):
    chat_id = message.chat.id
    db.insert_user_to_db(chat_id)

    homework_list = [f"{index + 1}. {item}\n" for index, item in enumerate(db.get_data_from_db(chat_id, columns="homework")[0][0].split(','))]
    homework = [i for i in homework_list if i != []]
    if not homework:
        bot.send_message(chat_id, "У вас нет домашнего задания")
        return
    bot.send_message(chat_id, "".join(homework))
    bot.send_message(chat_id, "Чтобы убрать дз из списка введите его номер")
    bot.register_next_step_handler(message, delete_homework)


def delete_homework(message):
    chat_id = message.chat.id
    nums = list(range(1, len(db.get_data_from_db(chat_id, columns="homework")[0][0].split(',')) - 1))
    if int(message.text) not in nums:
        bot.send_message(chat_id, "Нет такого номера дз")
        return
    curr_hw = db.get_data_from_db(chat_id, columns="homework")[0][0].split(',')[:-1]
    curr_hw.pop(int(message.text))
    db.update_db(chat_id, columns=("homework",), values=("".join(curr_hw),))


@bot.message_handler(commands=["get_homework"])#пока не работает
def get_homework(message):
    bot.send_message(message.chat.id, "Отправьте дз через запятую")
    bot.register_next_step_handler(message, add_homework_to_db)


def add_homework_to_db(message):
    db.insert_user_to_db(message.chat.id)
    db.update_db(chat_id=message.chat.id, columns=("homework",), values=(message.text + ',',), replace=True)
    bot.send_message(message.chat.id, "Дз получено")
    print(db.get_data_from_db(message.chat.id, columns="homework"))


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
            bot.send_message(chat_id, f"Напиши своё расписание на {day_week} в формате:\n{FORMAT_SCHEDULE}")

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


def run_polling():
    bot.polling()


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
