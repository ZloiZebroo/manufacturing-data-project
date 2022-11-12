import os
import requests

telegram_token = os.environ['tg_token']


def send_message(chat_id: int, text: str) -> None:
    method = 'SendMessage'
    url = f'https://api.telegram.org/bot{telegram_token}/{method}'
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    requests.post(url, data=data)