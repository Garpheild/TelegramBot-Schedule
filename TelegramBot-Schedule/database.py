import logging
import sqlite3
from config import *
import os


def create_table():
    try:
        with sqlite3.connect(DB_FILE_NAME) as con:
            cur = con.cursor()
            cur.execute('''
            CREATE TABLE IF NOT EXISTS user_data1(
            id INTEGER PRIMARY KEY,
            chat_id INTEGER,
            day_week TEXT, 
            id_lesson INTEGER, 
            lesson TEXT,
            homework TEXT DEFAULT "");
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
            FROM user_data1
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
                INSERT INTO user_data1(chat_id, day_week, id_lesson, lesson)
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
                   DELETE FROM user_data1 WHERE chat_id = {chat_id} AND day_week = "{day_week}";
                   ''')
            con.commit()
    except Exception as e:
        logging.error(e)


def get_data_from_db(chat_id, columns="chat_id"):
    try:
        with sqlite3.connect(DB_FILE_NAME) as con:
            cur = con.cursor()
            data = cur.execute(f'''
            SELECT {columns}
            FROM user_data 
            WHERE chat_id = {chat_id};
                ''')
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


if os.path.exists(DB_FILE_NAME):
    create_table()
