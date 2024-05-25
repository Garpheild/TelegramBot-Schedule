TG_TOKEN = "creds/telegram_token.txt"
LOGS = "logs.txt"
DB_FILE_NAME = "user_data.db"

USER_GPT_TOKEN_LIMIT = 1000
GPT_MAX_TOKENS = 100
GPT_MODEL = "yandexgpt-lite"
URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
FOLDER_ID = "creds/folder_id.txt"
IAM_TOKEN = "creds/iam_token.txt"

bot_answers = {
    "/start": "Добро пожаловать! Это бот - школьное расписание. В нём ты можешь хранить своё расписание "
              "на каждый школьный день, получать уведомление с напоминанием о дз и сохранять своё дз в чек-лист. Подробнее /help",
    "/help": "В боте 5 команд\n"
             "/add_schedule - добавляет или заменяет расписание на определенный день\n"
             "/sent_schedule - скидывает расписание на определенный день\n"
             "/setting_notification - настраивает уведомления с напоминанием о дз\n"
             "/get_homework - добавляет дз в чек-лист\n"
             "/sent_homework - отправляет чек-лист с дз\n"
             "/gpt_help - предоставляет персональную помощ от GPT"
}

FORMAT_SCHEDULE = "Урок1/Урок2/Урок3\n" \
                  "Например: Физика в 14 каб/Русский язык 8:50-9:30 и так далее (К урокам можно добавлять нужную " \
                  "информацию) "
