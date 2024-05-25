import logging
import requests
from config import GPT_MAX_TOKENS, URL, IAM_TOKEN, FOLDER_ID, GPT_MODEL

def get_answer(text):
    headers = {
        'Authorization': f'Bearer {get_creds(IAM_TOKEN)}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": f"gpt://{get_creds(FOLDER_ID)}/{GPT_MODEL}",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": GPT_MAX_TOKENS
        },

        "messages": [
            {
                "role": "user",
                "text": text
            }
        ]
    }

    response = requests.post(url=URL, headers=headers, json=data).json()

    if "error" not in response:
        return response["result"]["alternatives"][0]["message"]["text"], int(response["result"]["usage"]["completionTokens"])
    else:
        logging.error(response)
        return "Ошибка при генерации запроса", 0
