import logging
import sqlite3
from config import *


def create_table():
    try:
        with sqlite3.connect(DB_FILE_NAME) as con:
            cur = con.cursor()
            cur.execute('''
            CREATE TABLE IF NOT EXISTS user_data(
            id INTEGER PRIMARY KEY,
            chat_id INTEGER,
            day_week TEXT, 
            id_lesson INTEGER, 
            lesson TEXT,
            homework TEXT DEFAULT "",
            time_notification TEXT,
            day_notification TEXT DEFAULT "",
            used_gpt_tokens INTEGER DEFAULT 0);
                ''')
            con.commit()
    except Exception as e:
        logging.error(e)


def get_schedule(chat_id, day_week):
    try:
        with sqlite3.connect(DB_FILE_NAME) as con:
            cur = con.cursor()
            data = cur.execute(f'''
            SELECT id_lesson, lesson
            FROM user_data
            WHERE chat_id = {chat_id} AND day_week = "{day_week}"
            ORDER BY id_lesson ASC;
                ''')
            return [_ for _ in data]
    except Exception as e:
        logging.error(e)


def insert_schedule_to_db(chat_id: int, day_week: str, id_lesson: int, lesson: str):
    try:
        with sqlite3.connect(DB_FILE_NAME) as con:
            cur = con.cursor()
            cur.execute(f'''
                INSERT INTO user_data(chat_id, day_week, id_lesson, lesson)
                VALUES ({chat_id}, "{day_week}", {id_lesson}, "{lesson}");
                ''')
            con.commit()
    except Exception as e:
        logging.error(e)


def delete_schedule(chat_id, day_week):
    try:
        with sqlite3.connect(DB_FILE_NAME) as con:
            cur = con.cursor()
            cur.execute(f'''
                   DELETE FROM user_data WHERE chat_id = {chat_id} AND day_week = "{day_week}";
                   ''')
            con.commit()
    except Exception as e:
        logging.error(e)


def get_data_from_db(chat_id, columns="chat_id", notification_mode=False):
    try:
        with sqlite3.connect(DB_FILE_NAME) as con:
            cur = con.cursor()
            data = cur.execute(f'''
            SELECT {columns}
            FROM user_data 
            WHERE chat_id = {chat_id} AND {columns} != '' AND {columns} IS NOT NULL;
                ''')
            if notification_mode:
                return [row[0] for row in cur.fetchall()]
            return [_ for _ in data]
    except Exception as e:
        logging.error(e)


def insert_user_to_db(chat_id: int):
    try:
        with sqlite3.connect(DB_FILE_NAME) as con:
            cur = con.cursor()
            if not get_data_from_db(chat_id):
                cur.execute(f'''
                INSERT INTO user_data(chat_id)
                VALUES ({chat_id});
                ''')
                con.commit()
    except Exception as e:
        logging.error(e)


def update_db(chat_id, columns: tuple, values: tuple, replace=True):
    try:
        with sqlite3.connect(DB_FILE_NAME) as con:
            cur = con.cursor()
            for column, value in zip(columns, values):
                if replace:
                    cur.execute(f'UPDATE user_data SET {column} = ? WHERE chat_id = {chat_id};', (value,))
                else:
                    cur.execute(f'UPDATE user_data SET {column} = {column} || ? WHERE chat_id = {chat_id};', (value,))
        con.commit()
    except Exception as e:
        logging.error(e)


def add_day(chat_id, day):
    try:
        with sqlite3.connect(DB_FILE_NAME) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO user_data (chat_id, day_notification) VALUES (?, ?)", (chat_id, day))
            conn.commit()
    except Exception as e:
        logging.error(e)


def remove_day(chat_id, day):
    try:
        with sqlite3.connect(DB_FILE_NAME) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM user_data WHERE chat_id = ? AND day_notification = ?", (chat_id, day))
            conn.commit()
    except Exception as e:
        logging.error(e)


def select_notification():
    try:
        with sqlite3.connect(DB_FILE_NAME) as con:
            c = con.cursor()
            c.execute(f'''
            SELECT chat_id, time_notification, day_notification
               FROM user_data
               WHERE day_notification != ""
               AND time_notification IS NOT NULL;
                ''')
            return [row for row in c.fetchall()]
    except Exception as e:
        logging.error(e)


create_table()
