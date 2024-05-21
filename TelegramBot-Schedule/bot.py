import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

from get_creds import get_telegram_token
from config import Path, bot_answers

bot = Bot(token=get_telegram_token())
dp = Dispatcher()
logging.basicConfig(filename=Path.LOGS, level=logging.INFO,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")


@dp.message(Command("start"))
@dp.message(Command("help"))
async def cmd_start(message: types.Message):
    await message.answer(bot_answers[message.text])


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.info("Бот запущен")
    print("Бот выключен")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот выключен")
        print("Бот выключен")
